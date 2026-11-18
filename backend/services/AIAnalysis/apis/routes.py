from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from typing import Dict, Optional, Any
import asyncio

from services.AIAnalysis.db import get_database as get_analysis_db, AnalysisRecord
from services.AIFormFilling.src.db.connection import get_database as get_grievance_db
from services.AIAnalysis.shared.schemas import GrievanceData, AnalysisResult
from services.AIAnalysis.agents import (
    VectorEmbeddingAgent,
    PriorityScorerAgent,
    SmartRoutingAgent,
    NotificationDispatcherAgent,
    DocumentAnalysisAgent,
    LocationIntelligenceAgent
)
from services.civic_operations import register_complaint

router = APIRouter()

# Initialize agents
vector_agent = VectorEmbeddingAgent()
priority_agent = PriorityScorerAgent()
routing_agent = SmartRoutingAgent()
notification_agent = NotificationDispatcherAgent()
document_agent = DocumentAnalysisAgent()
location_agent = LocationIntelligenceAgent()

async def monitor_grievance_submissions():
    """
    Background worker that polls the grievance_forms collection every minute
    for new submissions with status 'submitted' and triggers analysis pipeline.
    """
    db = get_grievance_db()  # Synchronous call
    collection = db.grievance_forms
    
    while True:
        try:
            print("Polling for new grievances...")
            # Query for documents with status 'submitted'
            cursor = collection.find({"status": "submitted"})
            async for doc in cursor:
                form_id = doc.get("form_id") or str(doc.get("_id", "unknown"))
                print(f"Processing new grievance: {form_id}")
                
                try:
                    cat1 = doc.get("CATEGORY_1") if isinstance(doc.get("CATEGORY_1"), dict) else {}
                    cat2 = doc.get("CATEGORY_2") if isinstance(doc.get("CATEGORY_2"), dict) else {}
                    cat3 = doc.get("CATEGORY_3") if isinstance(doc.get("CATEGORY_3"), dict) else {}
                    cat4 = doc.get("CATEGORY_4") if isinstance(doc.get("CATEGORY_4"), dict) else {}

                    full_desc = (
                        doc.get("full_description")
                        or cat3.get("full_description")
                        or doc.get("description")
                        or doc.get("original_text")
                        or "No description provided."
                    )
                    title = doc.get("title") or cat1.get("title") or "Grievance Report"
                    category = doc.get("category") or cat1.get("category") or "Other"
                    area_ward_name = doc.get("area_ward_name") or cat2.get("area_ward_name")
                    landmark = doc.get("landmark") or cat2.get("landmark")
                    location_hint = doc.get("location_hint") or cat2.get("location_hint")
                    geo_coordinates = doc.get("geo_coordinates") or cat2.get("geo_coordinates")
                    impacted_population = (
                        doc.get("impacted_population")
                        or cat4.get("impacted_population")
                        or "Street"
                    )
                    is_recurring = doc.get("is_recurring")
                    if is_recurring is None:
                        is_recurring = cat4.get("is_recurring", False)

                    # Extract GrievanceData from document with fallbacks
                    grievance = GrievanceData(
                        form_id=form_id,
                        user_id=str(doc.get("user_id") or ""),
                        title=str(title),
                        full_description=str(full_desc),
                        category=str(category),
                        area_ward_name=area_ward_name,
                        impacted_population=str(impacted_population),
                        is_recurring=bool(is_recurring),
                        document_paths=doc.get("document_paths") or [],
                        landmark=landmark,
                        location_hint=location_hint,
                        geo_coordinates=geo_coordinates,
                    )
                    
                    # Run analysis pipeline
                    await run_analysis_pipeline(grievance)
                except Exception as doc_err:
                    print(f"Error processing grievance {form_id}: {doc_err}")
                    # Update status so one malformed document does not indefinitely poison the worker queue
                    try:
                        await collection.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"status": "error", "error_reason": str(doc_err)}}
                        )
                    except Exception as update_err:
                        print(f"Failed to update error status for {form_id}: {update_err}")
            
            # Wait for 60 seconds before next poll
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"Error in grievance monitoring: {e}")
            await asyncio.sleep(60)  # Wait before retrying

@router.get("/")
async def root():
    return {
        "service": "AI Analysis Service",
        "status": "running",
        "version": "1.0.0"
    }

@router.post("/analyze", response_model=Dict)
async def analyze_grievance(
    grievance: GrievanceData,
    background_tasks: BackgroundTasks
):
    """
    Main endpoint to trigger the analysis pipeline.
    Called by AIFormFilling service after form submission.
    """
    try:
        # Run analysis in background
        background_tasks.add_task(
            run_analysis_pipeline,
            grievance
        )
        
        return {
            "status": "accepted",
            "message": "Analysis pipeline initiated",
            "form_id": grievance.form_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_pipeline(grievance: GrievanceData):
    """
    Execute the multi-agent analysis pipeline
    """
    try:
        # Module 0: Location Intelligence Agent (Ground vague location to coordinates & ward)
        print(f"[LOC] Grounding location: {grievance.form_id}")
        loc_intelligence = await location_agent.resolve_location(
            area_ward_name=grievance.area_ward_name,
            landmark=grievance.landmark,
            location_hint=grievance.location_hint,
            title=grievance.title,
            description=grievance.full_description,
        )
        grievance.area_ward_name = loc_intelligence.get("area_ward_name") or grievance.area_ward_name
        grievance.geo_coordinates = loc_intelligence.get("geo_coordinates")

        # Module A: Vector Embedding & Duplicate Check
        print(f"[A] Checking for duplicates: {grievance.form_id}")
        vector_check = await vector_agent.check_duplicate(grievance)
        
        # Module B: Priority Scorer
        print(f"[B] Scoring priority: {grievance.form_id}")
        priority_score = await priority_agent.score_priority(grievance)
        
        # Module C: Smart Routing
        print(f"[C] Routing to department: {grievance.form_id}")
        routing = await routing_agent.route_grievance(
            grievance, 
            priority_score.urgency_level
        )
        
        # Determine final status
        if vector_check.is_duplicate:
            status = "Linked"
        else:
            status = "Assigned"
        
        # Module D: Document Analysis
        print(f"[D] Analyzing documents: {grievance.form_id}")
        document_insights = await document_agent.analyze_documents(grievance.document_paths)
        
        # Create analysis result
        analysis_result = AnalysisResult(
            form_id=grievance.form_id,
            vector_check=vector_check,
            priority_score=priority_score,
            routing=routing,
            status=status,
            analyzed_at=datetime.utcnow(),
            document_insights=document_insights,
            location_intelligence=loc_intelligence,
        )
        
        # Module E: Notification Dispatch
        print(f"[E] Dispatching notifications: {grievance.form_id}")
        await notification_agent.dispatch_notifications(analysis_result)
        
        # Create citizen message for DB storage
        if analysis_result.vector_check.is_duplicate:
            citizen_message = (
                f"Your grievance #{analysis_result.form_id} has been linked to an existing case "
                f"#{analysis_result.vector_check.parent_form_id}. You'll receive updates on the resolution."
            )
        else:
            citizen_message = (
                f"Your grievance #{analysis_result.form_id} has been assigned to "
                f"{analysis_result.routing.officer_name} ({analysis_result.routing.department}). "
                f"Expected response time: {analysis_result.routing.estimated_response_time}."
            )
        
        # Store analysis record in database
        await save_analysis_record(grievance, analysis_result)
        
        # Update grievance form status in AIFormFilling database
        await update_grievance_status(
            grievance.form_id,
            status,
            analysis_result,
            citizen_message,
            grievance.geo_coordinates,
            grievance.area_ward_name
        )
        await register_complaint(
            grievance.form_id,
            grievance.model_dump(),
            {
                "status": status,
                "priority_score": analysis_result.priority_score.score,
                "urgency_level": analysis_result.priority_score.urgency_level,
                "assigned_department": analysis_result.routing.department,
                "assigned_officer_id": analysis_result.routing.officer_id,
                "assigned_officer_name": analysis_result.routing.officer_name,
            },
        )
        
        print(f"✅ Analysis pipeline completed for {grievance.form_id}")
        
    except Exception as e:
        print(f"❌ Error in analysis pipeline for {grievance.form_id}: {e}")
        # Log error but don't raise to avoid breaking background task

async def save_analysis_record(grievance: GrievanceData, analysis: AnalysisResult):
    """Save analysis record to database"""
    db = get_analysis_db()  # Synchronous call
    
    record = AnalysisRecord(
        form_id=analysis.form_id,
        user_id=grievance.user_id,
        is_duplicate=analysis.vector_check.is_duplicate,
        parent_form_id=analysis.vector_check.parent_form_id,
        similarity_score=analysis.vector_check.similarity_score,
        priority_score=analysis.priority_score.score,
        priority_reasoning=analysis.priority_score.reasoning,
        urgency_level=analysis.priority_score.urgency_level,
        assigned_department=analysis.routing.department,
        assigned_officer_id=analysis.routing.officer_id,
        assigned_officer_name=analysis.routing.officer_name,
        estimated_response_time=analysis.routing.estimated_response_time,
        status=analysis.status,
        analyzed_at=analysis.analyzed_at,
        location_intelligence=analysis.location_intelligence,
        geo_coordinates=grievance.geo_coordinates
    )
    
    await db.analysis_records.insert_one(record.model_dump())

async def update_grievance_status(
    form_id: str, 
    status: str, 
    analysis: AnalysisResult,
    citizen_message: str,
    geo_coordinates: Optional[Dict[str, float]] = None,
    area_ward_name: Optional[str] = None
):
    """Update grievance form in AIFormFilling database"""
    db = get_grievance_db()  # Synchronous call
    
    update_data = {
        "status": status,  # Changed to use the passed status ("assigned" or "linked")
        "analyzed_at": analysis.analyzed_at,
        "priority_score": analysis.priority_score.score,
        "priority_reasoning": analysis.priority_score.reasoning,  # Added for citizen info
        "urgency_level": analysis.priority_score.urgency_level,
        "assigned_department": analysis.routing.department,
        "assigned_officer_id": analysis.routing.officer_id,
        "assigned_officer_name": analysis.routing.officer_name,
        "estimated_response_time": analysis.routing.estimated_response_time,
        "message": citizen_message,  # Added message field
        "document_insights": analysis.document_insights,  # Added for citizen info
        "location_intelligence": analysis.location_intelligence
    }
    
    if geo_coordinates:
        update_data["geo_coordinates"] = geo_coordinates
    if area_ward_name:
        update_data["area_ward_name"] = area_ward_name
    
    if analysis.vector_check.is_duplicate:
        update_data["parent_form_id"] = analysis.vector_check.parent_form_id
        update_data["similarity_score"] = analysis.vector_check.similarity_score  # Added for citizen info
    
    await db.grievance_forms.update_one(
        {"form_id": form_id},
        {"$set": update_data}
    )

@router.get("/analysis/{form_id}")
async def get_analysis(form_id: str):
    """Retrieve analysis record for a form"""
    db = get_analysis_db()  # Synchronous call
    
    record = await db.analysis_records.find_one({"form_id": form_id})
    
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    record["_id"] = str(record["_id"])
    return record

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AIAnalysis"}
