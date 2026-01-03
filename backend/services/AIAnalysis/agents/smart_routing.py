import httpx
from typing import Dict, Optional
from services.AIAnalysis.shared.schemas import GrievanceData, RoutingResult
from services.AIAnalysis.utils.config import settings

class SmartRoutingAgent:
    def __init__(self):
        self.user_service_url = settings.USER_SERVICE_URL
        
        # Department mapping
        self.department_mapping = {
            "Electricity": "Electrical Department",
            "Water Supply": "Water Works Department",
            "Roads": "Public Works Department",
            "Sanitation": "Sanitation Department",
            "Street Lights": "Electrical Department",
            "Drainage": "Sanitation Department",
            "Public Safety": "Municipal Police",
            "Parks": "Horticulture Department",
            "Buildings": "Building Department"
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
        Query User Service to find the nodal officer
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/officers/nodal",
                    params={
                        "department": department,
                        "area_ward": area_ward_name
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "officer_id": data.get("officer_id", "DEFAULT_OFFICER"),
                        "officer_name": data.get("name", "Nodal Officer")
                    }
        except Exception as e:
            print(f"Error finding nodal officer: {e}")
        
        # Fallback to default officer
        return {
            "officer_id": "DEFAULT_OFFICER",
            "officer_name": f"{department} - Nodal Officer"
        }
