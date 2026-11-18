import httpx
import re
import logging
from typing import Dict, Optional
from services.AIAnalysis.shared.schemas import GrievanceData, RoutingResult
from services.AIAnalysis.utils.config import settings
from services.superuser_services.db.connection import get_database as get_superuser_db

logger = logging.getLogger(__name__)

class SmartRoutingAgent:
    def __init__(self):
        # Department mapping
        self.department_mapping = {
            "Electricity": "Electricity",
            "Water Supply": "Water Supply",
            "Water": "Water Supply",
            "Roads": "Roads",
            "Sanitation": "Sanitation",
            "Street Lights": "Electricity",
            "Drainage": "Drainage",
            "Public Safety": "Public Safety",
            "Parks": "Sanitation",
            "Buildings": "Roads"
        }
        
        # Estimated response times by urgency
        self.response_times = {
            "critical": "2 hours",
            "high": "12 hours",
            "medium": "24 hours",
            "low": "48 hours"
        }
    
    def _normalize_department(self, raw_category: Optional[str]) -> str:
        """Fuzzy normalizes raw complaint category to canonical municipal department"""
        if not raw_category:
            return "Sanitation"
        cat_lower = str(raw_category).lower()
        if any(w in cat_lower for w in ["garbage", "waste", "trash", "sanitation", "clean", "sweeper", "dustbin", "environment", "health", "dump", "smell", "animal", "foul", "decay"]):
            return "Sanitation"
        if any(w in cat_lower for w in ["water", "leak", "pipe", "tap", "supply"]):
            return "Water Supply"
        if any(w in cat_lower for w in ["drain", "sewer", "gutter", "overflow", "manhole"]):
            return "Drainage"
        if any(w in cat_lower for w in ["light", "power", "electric", "current", "wire", "pole", "transformer"]):
            return "Electricity"
        if any(w in cat_lower for w in ["road", "pothole", "tar", "footpath", "highway", "traffic"]):
            return "Roads"
        if any(w in cat_lower for w in ["safety", "crime", "stray", "police", "danger", "hazard"]):
            return "Public Safety"
        return self.department_mapping.get(raw_category, "Sanitation")

    async def route_grievance(
        self, 
        grievance: GrievanceData, 
        urgency_level: str
    ) -> RoutingResult:
        """
        Route grievance to appropriate department and officer
        """
        # Get normalized department from category or description
        department = self._normalize_department(grievance.category)
        if department == "Sanitation" and not grievance.category:
            # Fallback to scanning title and description
            combined = f"{grievance.title} {grievance.full_description}".lower()
            department = self._normalize_department(combined)
        
        # Find nodal officer for this department and area
        officer = await self._find_nodal_officer(
            department=department,
            area_ward_name=grievance.area_ward_name
        )
        
        # Get estimated response time
        eta = self.response_times.get(urgency_level, "24 hours")
        
        return RoutingResult(
            department=department,
            officer_id=officer["officer_id"],
            officer_name=officer["officer_name"],
            estimated_response_time=eta
        )
    
    async def _find_nodal_officer(
        self, 
        department: str, 
        area_ward_name: str
    ) -> Dict[str, str]:
        """
        Query SuperUser DB staff_users collection to find the nodal officer.
        Uses multi-tier matching:
         1. Match department regex + fuzzy ward regex
         2. Match department regex (any ward in jurisdiction)
         3. Fallback to default department officer
        """
        try:
            db = get_superuser_db()
            collection = db.staff_users

            # Regex for department (e.g. 'Water' matches 'Water' and 'Water Supply')
            dept_key = "Water" if "water" in department.lower() else department
            dept_regex = {"$regex": f".*{re.escape(dept_key)}.*", "$options": "i"}

            # Tier 1: Try matching both department and ward
            if area_ward_name and area_ward_name.strip():
                clean_ward = area_ward_name.split("-")[-1].strip()
                ward_term = clean_ward if len(clean_ward) >= 3 else area_ward_name.strip()
                query = {
                    "role": "NODAL_OFFICER",
                    "metadata.dept": dept_regex,
                    "metadata.ward": {"$regex": f".*{re.escape(ward_term)}.*", "$options": "i"}
                }
                officer_doc = await collection.find_one(query)
                if officer_doc:
                    return {
                        "officer_id": str(officer_doc.get("_id")),
                        "officer_name": officer_doc.get("full_name", f"{department} - Nodal Officer")
                    }

            # Tier 2: Try matching department for any ward
            officer_doc = await collection.find_one({
                "role": "NODAL_OFFICER",
                "metadata.dept": dept_regex
            })
            if officer_doc:
                return {
                    "officer_id": str(officer_doc.get("_id")),
                    "officer_name": officer_doc.get("full_name", f"{department} - Nodal Officer")
                }

            # Tier 3: Any active nodal officer
            any_officer = await collection.find_one({"role": "NODAL_OFFICER"})
            if any_officer:
                return {
                    "officer_id": str(any_officer.get("_id")),
                    "officer_name": any_officer.get("full_name", f"{department} - Nodal Officer")
                }

        except Exception as e:
            logger.exception("Error finding nodal officer in DB: %s", e)
        
        # Fallback to default officer
        return {
            "officer_id": "DEFAULT_OFFICER",
            "officer_name": f"{department} - Nodal Officer"
        }
