from services.superuser_services.models.staff_user import StaffUser, UserRole, Department, StaffMetadata, AccountStatus
from services.superuser_services.db.repositories.user_repository import user_repository
from services.superuser_services.utils.auth import auth_utils
from services.superuser_services.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)

async def create_initial_superadmin():
    """Create initial SuperAdmin user if not exists"""
    try:
        existing_admin = await user_repository.get_user_by_email(settings.initial_admin_email)
        if existing_admin:
            logger.info("SuperAdmin already exists")
            return
        
        staff_id = f"SUPER_{uuid.uuid4().hex[:6].upper()}"
        hashed_password = auth_utils.hash_password(settings.initial_admin_password)
        
        superadmin = StaffUser(
            staff_id=staff_id,
            full_name="System SuperAdmin",
            employee_id="SUPER_ADMIN_001",
            email=settings.initial_admin_email,
            phone_number="+911234567890",
            password_hash=hashed_password,
            role=UserRole.SUPER_ADMIN,
            metadata=StaffMetadata(
                dept=Department.ELECTRICITY,
                ward="System",
                designation="System Administrator"
            ),
            account_status=AccountStatus(
                is_active=True,
                is_first_login=False,
                created_by="SYSTEM"
            )
        )
        
        await user_repository.create_user(superadmin)
        logger.info(f"SuperAdmin created successfully with ID: {staff_id}")
        logger.info(f"SuperAdmin credentials - Email: {settings.initial_admin_email}, Password: {settings.initial_admin_password}")
        
    except Exception as e:
        logger.error(f"Error creating SuperAdmin: {e}")
        raise

async def seed_sample_data():
    """Create sample department admins and nodal officers for all key civic departments"""
    try:
        sample_officers = [
            {
                "full_name": "Ramesh Verma",
                "employee_id": "SAN_OFF_001",
                "email": "ramesh.sanitation@gov.in",
                "phone_number": "+919876500001",
                "role": UserRole.NODAL_OFFICER,
                "dept": Department.SANITATION,
                "ward": "Sector 14",
                "designation": "Sanitation Inspector"
            },
            {
                "full_name": "Pooja Iyer",
                "employee_id": "WAT_OFF_001",
                "email": "pooja.water@gov.in",
                "phone_number": "+919876500002",
                "role": UserRole.NODAL_OFFICER,
                "dept": Department.WATER_SUPPLY,
                "ward": "Sector 14",
                "designation": "Water Works Engineer"
            },
            {
                "full_name": "Vikram Singh",
                "employee_id": "ROA_OFF_001",
                "email": "vikram.roads@gov.in",
                "phone_number": "+919876500003",
                "role": UserRole.NODAL_OFFICER,
                "dept": Department.ROADS,
                "ward": "Ward 14",
                "designation": "Assistant Engineer (PWD)"
            },
            {
                "full_name": "Rahul Sharma",
                "employee_id": "ELEC_OFF_001",
                "email": "rahul.sharma@gov.in",
                "phone_number": "+919876500004",
                "role": UserRole.NODAL_OFFICER,
                "dept": Department.ELECTRICITY,
                "ward": "Shanti Nagar",
                "designation": "Junior Engineer (Power)"
            },
            {
                "full_name": "Amit Patel",
                "employee_id": "SAF_OFF_001",
                "email": "amit.safety@gov.in",
                "phone_number": "+919876500005",
                "role": UserRole.NODAL_OFFICER,
                "dept": Department.PUBLIC_SAFETY,
                "ward": "Central Zone",
                "designation": "Public Safety Officer"
            },
            {
                "full_name": "Sunil Rao",
                "employee_id": "DRN_OFF_001",
                "email": "sunil.drainage@gov.in",
                "phone_number": "+919876500006",
                "role": UserRole.NODAL_OFFICER,
                "dept": Department.DRAINAGE,
                "ward": "Central Zone",
                "designation": "Drainage Supervisor"
            },
            {
                "full_name": "Electricity Dept Admin",
                "employee_id": "ELEC_ADMIN_001",
                "email": "elec.admin@gov.in",
                "phone_number": "+919876500099",
                "role": UserRole.DEPT_ADMIN,
                "dept": Department.ELECTRICITY,
                "ward": "Central Zone",
                "designation": "Electrical Superintendent"
            }
        ]

        for off in sample_officers:
            if not await user_repository.get_user_by_email(off["email"]):
                staff_id = f"STF_{uuid.uuid4().hex[:6].upper()}"
                user = StaffUser(
                    staff_id=staff_id,
                    full_name=off["full_name"],
                    employee_id=off["employee_id"],
                    email=off["email"],
                    phone_number=off["phone_number"],
                    password_hash=auth_utils.hash_password("Officer@123"),
                    role=off["role"],
                    metadata=StaffMetadata(
                        dept=off["dept"],
                        ward=off["ward"],
                        designation=off["designation"]
                    ),
                    account_status=AccountStatus(
                        is_active=True,
                        is_first_login=False,
                        created_by="SYSTEM"
                    )
                )
                await user_repository.create_user(user)
                logger.info("Seeded staff officer: %s (%s, %s)", off["full_name"], off["dept"], off["ward"])

    except Exception as e:
        logger.error(f"Error seeding sample data: {e}")
