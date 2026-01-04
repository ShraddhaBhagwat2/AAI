from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from ..services.officer_service import OfficerService
from ..schemas.requests import UpdateStatusRequest, ClarificationRequest, ResolveTicketRequest
from ..schemas.responses import DashboardView, StatusUpdateResponse, ClarificationResponse, ResolutionResponse, ClarificationsListResponse, TicketCountsResponse
from ..utils.file_handler import file_handler
from ...superuser_services.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/officer", tags=["Officer Resolution"])

# Define officer role requirement
get_current_officer = require_role(["NODAL_OFFICER", "SUPER_ADMIN", "DEPT_ADMIN"])  # Use actual roles: NODAL_OFFICER for officers

@router.get("/dashboard", response_model=List[DashboardView])
async def get_officer_dashboard(current_officer: dict = Depends(get_current_officer)):
    """Get officer's dashboard with all assigned tickets"""
    officer_service = OfficerService()  # Instantiate here
    try:
        dashboard_data = await officer_service.get_officer_dashboard(current_officer["sub"])  # Use "sub" for user ID
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update-status", response_model=StatusUpdateResponse)
async def update_ticket_status(
    request: UpdateStatusRequest,
    current_officer: dict = Depends(get_current_officer)
):
    """Update ticket status (Assigned -> In Progress, etc.)"""
    officer_service = OfficerService()  # Instantiate here
    try:
        result = await officer_service.update_ticket_status(
            officer_id=current_officer["sub"],  # Use "sub" for user ID
            grievance_id=request.grievance_id,
            new_status=request.new_status,
            progress_note=request.progress_note
        )
        
        return StatusUpdateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/resolved", response_model=List[DashboardView])
async def get_resolved_tickets(current_officer: dict = Depends(get_current_officer)):
    """Get all resolved tickets for the officer"""
    officer_service = OfficerService()  # Instantiate here
    try:
        result = await officer_service.get_resolved_tickets(current_officer["sub"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/request-clarification", response_model=ClarificationResponse)
async def request_clarification(
    request: ClarificationRequest,
    current_officer: dict = Depends(get_current_officer)
):
    """Send clarification request to citizen"""
    officer_service = OfficerService()  # Instantiate here
    try:
        result = await officer_service.request_clarification(
            officer_id=current_officer["sub"],  # Use "sub" for user ID
            grievance_id=request.grievance_id,
            message=request.message
        )
        
        return ClarificationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve", response_model=ResolutionResponse)
async def resolve_ticket(
    grievance_id: str = Form(...),
    action_taken: str = Form(...),
    closing_remark: str = Form(...),
    resolution_photos: List[UploadFile] = File(...),
    current_officer: dict = Depends(get_current_officer)
):
    """Resolve ticket with mandatory proof photos"""
    officer_service = OfficerService()  # Instantiate here
    try:
        # Validate files
        if not resolution_photos:
            raise HTTPException(status_code=400, detail="Resolution photos are mandatory")
        
        # Save uploaded photos
        photo_paths = await file_handler.save_resolution_photos(
            files=resolution_photos,
            officer_id=current_officer["sub"],  # Use "sub" for user ID
            grievance_id=grievance_id
        )
        
        # Resolve ticket
        result = await officer_service.resolve_ticket(
            officer_id=current_officer["sub"],  # Use "sub" for user ID
            grievance_id=grievance_id,
            action_taken=action_taken,
            closing_remark=closing_remark,
            resolution_photos=photo_paths
        )
        
        return ResolutionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticket/{grievance_id}", response_model=DashboardView)
async def get_ticket_details(
    grievance_id: str,
    current_officer: dict = Depends(get_current_officer)
):
    """Get detailed view of a specific ticket"""
    officer_service = OfficerService()  # Instantiate here
    try:
        tickets = await officer_service.get_officer_dashboard(current_officer["sub"])  # Use "sub" for user ID
        ticket = next((t for t in tickets if t.ticket.grievance_id == grievance_id), None)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clarifications", response_model=ClarificationsListResponse)
async def get_clarifications(current_officer: dict = Depends(get_current_officer)):
    """Get all clarifications requested by the officer"""
    officer_service = OfficerService()  # Instantiate here
    try:
        result = await officer_service.get_clarifications(current_officer["sub"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/total", response_model=TicketCountsResponse)
async def get_ticket_counts(current_officer: dict = Depends(get_current_officer)):
    """Get total counts of tickets by status for the officer"""
    officer_service = OfficerService()  # Instantiate here
    try:
        result = await officer_service.get_ticket_counts(current_officer["sub"])
        return TicketCountsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/start", response_model=StatusUpdateResponse)
async def start_ticket_work(
    request: UpdateStatusRequest,
    current_officer: dict = Depends(get_current_officer)
):
    """Convenience endpoint to mark a ticket as in_progress (start work)"""
    officer_service = OfficerService()
    try:
        result = await officer_service.update_ticket_status(
            officer_id=current_officer["sub"],
            grievance_id=request.grievance_id,
            new_status="in_progress",
            progress_note=request.progress_note
        )
        return StatusUpdateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/pause", response_model=StatusUpdateResponse)
async def pause_ticket_work(
    request: UpdateStatusRequest,
    current_officer: dict = Depends(get_current_officer)
):
    """Convenience endpoint to mark a ticket as paused"""
    officer_service = OfficerService()
    try:
        result = await officer_service.update_ticket_status(
            officer_id=current_officer["sub"],
            grievance_id=request.grievance_id,
            new_status="paused",
            progress_note=request.progress_note
        )
        return StatusUpdateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/resume", response_model=StatusUpdateResponse)
async def resume_ticket_work(
    request: UpdateStatusRequest,
    current_officer: dict = Depends(get_current_officer)
):
    """Convenience endpoint to resume work (set to in_progress)"""
    officer_service = OfficerService()
    try:
        result = await officer_service.update_ticket_status(
            officer_id=current_officer["sub"],
            grievance_id=request.grievance_id,
            new_status="in_progress",
            progress_note=request.progress_note
        )
        return StatusUpdateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OfficerResolutionService"}
