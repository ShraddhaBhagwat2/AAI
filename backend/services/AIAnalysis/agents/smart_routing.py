import httpx
from typing import Dict, Optional
from services.AIAnalysis.shared.schemas import GrievanceData, RoutingResult
from services.AIAnalysis.utils.config import settings
from services.superuser_services.db.connection import get_database as get_superuser_db

class SmartRoutingAgent:
    def __init__(self):
        
        # Department mapping
        self.department_mapping = {
            "Electricity": "Electricity",
            "Water Supply": "Water Supply",
            "Roads": "Roads",
            "Sanitation": "Sanitation",
            "Street Lights": "Street Lights",
            "Drainage": "Drainage",
            "Public Safety": "Public Safety",
            "Parks": "Parks",
            "Buildings": "Buildings"
        }
        
        # Estimated response times by urgency
        self.response_times = {
            "critical": "2 hours",
            "high": "12 hours",
            "medium": "24 hours",
            "low": "48 hours"
        }
    
    async def route_grievance(
        self, 
        grievance: GrievanceData, 
        urgency_level: str
    ) -> RoutingResult:
        """
        Route grievance to appropriate department and officer
        """
        # Get department from category
        department = self.department_mapping.get(
            grievance.category, 
            "General Administration"
        )
        
        # Find nodal officer for this department and area
        officer = await self._find_nodal_officer(
            department=department,
            area_ward_name=grievance.area_ward_name
        )
        
        # Get estimated response time
        eta = self.response_times.get(urgency_level, "48 hours")
        
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
        Query SuperUser DB staff_users collection to find the nodal officer
        """
        try:
            db = get_superuser_db()  # Synchronous call
            collection = db.staff_users
            
            # Query for nodal officer with matching dept and ward
            officer_doc = await collection.find_one({
                "role": "NODAL_OFFICER",
                "metadata.dept": department,
                "metadata.ward": area_ward_name
            })
            
            if officer_doc:
                return {
                    "officer_id": officer_doc["_id"],
                    "officer_name": officer_doc["full_name"]
                }
        except Exception as e:
            print(f"Error finding nodal officer in DB: {e}")
        
        # Fallback to default officer
        return {
            "officer_id": "DEFAULT_OFFICER",
            "officer_name": f"{department} - Nodal Officer"
        }
