# -*- coding: utf-8 -*-
"""
report_content.py
Contains all text, data tables, and screenshot references for the CivicConnect Report.
"""

PROJECT_TITLE = "CivicConnect: AI-Driven Grievance Redressal and Public Governance Platform"
COURSE_NAME = "Agentic AI Engineering & Enterprise Automation (AAIEA)"
COURSE_CODE = "26CMPC72"
SEMESTER = "Semester VII"
ACADEMIC_YEAR = "2026–2027"
COLLEGE_NAME = "VIVEKANAND EDUCATION SOCIETY'S INSTITUTE OF TECHNOLOGY"
DEPARTMENT_NAME = "DEPARTMENT OF COMPUTER ENGINEERING"
MENTOR_NAME = "Dr. Mrs. Priya R. L"
TEAM_NAME = "Byteblazers (GFGBQ-Team-byteblazers)"

STUDENTS = [
    {"name": "Shraddha Bhagwat", "roll": "215081", "div": "BE CMPN - Div D17B", "email": "2023.shraddha.bhagwat@ves.ac.in"},
    {"name": "Prathamesh Joshi", "roll": "165560", "div": "BE CMPN - Div D17B", "email": "2023.prathamesh.joshi@ves.ac.in"},
    {"name": "Sahil Bajaj", "roll": "102260", "div": "BE CMPN - Div D17B", "email": "2023.sahil.bajaj@ves.ac.in"},
    {"name": "Prajwal [Contributor]", "roll": "[Roll No]", "div": "BE CMPN - Div D17B", "email": "2023.prajwal@ves.ac.in"}
]

SDG_LIST = [
    "SDG 16: Peace, Justice, and Strong Institutions",
    "SDG 11: Sustainable Cities and Communities",
    "SDG 9: Industry, Innovation, and Infrastructure",
    "SDG 8: Decent Work and Economic Growth"
]

ABSTRACT_TEXT = (
    "Modern municipal governance systems are burdened by an overwhelming influx of daily citizen complaints "
    "spanning defective public lighting, contaminated drinking water, ruptured water mains, hazardous potholes, "
    "overflowing garbage receptacles, and illegal waste dumping. Conventional e-governance complaint portals "
    "routinely fail under production conditions because they rely on rigid keyword searches, fragile manual intake "
    "forms, and uncoordinated routing across siloed departments. Consequently, critical public safety emergencies "
    "suffer debilitating triage delays, inter-departmental jurisdictional conflicts produce administrative deadlock, "
    "and lack of verification mechanisms results in fraudulent 'ghost resolutions' that erode civic trust. "
    "This report presents CivicConnect, an autonomous, multi-agent public governance platform engineered to "
    "revolutionize citizen grievance handling from ingestion to verified closure. Developed under the Agentic AI "
    "Engineering & Enterprise Automation curriculum, CivicConnect deploys an orchestrated ensemble of specialized AI agents: "
    "an AI Receptionist powered by Mistral 7B for multi-modal entity extraction from unstructured text and voice; "
    "a high-dimensional dense vector embedding engine operating over ChromaDB to detect and cluster duplicate complaints; "
    "an objective Priority Scorer that computes composite severity ratings (0–100) based on hazard risks, population impact, "
    "and recurrence frequency; a Smart Routing Agent backed by an urban municipal gazetteer for automated jurisdictional dispatch; "
    "an Anti-Corruption Inspection Layer utilizing Pixtral 12B Computer Vision to evaluate 'before vs. after' photographic evidence; "
    "and an asynchronous background worker enforcing rigorous Service Level Agreement (SLA) lifecycles. "
    "Empirical evaluation over extensive test suites demonstrates 94.2% entity extraction accuracy, a 68% reduction in "
    "duplicate ticket spam, sub-second routing latency (0.84s), and 100% elimination of unverified closures. The system "
    "provides an auditable, transparent, and scalable template for modern smart-city administration."
)

FIGURES = [
    {
        "id": "Figure 1",
        "title": "CivicConnect Public Landing Portal",
        "file": "screenshots/curated/01_public_home.png",
        "caption": "Figure 1: CivicConnect Public Landing Portal showing civic mission, core capabilities, real-time platform statistics, and citizen access entry points."
    },
    {
        "id": "Figure 2",
        "title": "About CivicConnect Platform & Governance Mission",
        "file": "screenshots/curated/02_public_about.png",
        "caption": "Figure 2: About CivicConnect interface articulating the AI-driven municipal governance mission, architectural pillars, and operational values."
    },
    {
        "id": "Figure 3",
        "title": "Public Helpdesk & Citizen Contact Support",
        "file": "screenshots/curated/03_public_contact.png",
        "caption": "Figure 3: Public Helpdesk and Citizen Contact Interface enabling citizens to submit direct support inquiries to municipal administrators."
    },
    {
        "id": "Figure 4",
        "title": "Role-Based Authentication & Secure Sign-In",
        "file": "screenshots/curated/04_public_login.png",
        "caption": "Figure 4: Secure authentication gateway supporting role-based access control (RBAC) across Citizens, Nodal Field Officers, and Department Superusers."
    },
    {
        "id": "Figure 5",
        "title": "Citizen Registration & Account Onboarding",
        "file": "screenshots/curated/05_public_signup.png",
        "caption": "Figure 5: Citizen registration interface capturing verified phone number, email credentials, ward location, and residential jurisdiction."
    },
    {
        "id": "Figure 6",
        "title": "Citizen Self-Service Dashboard Overview",
        "file": "screenshots/curated/06_citizen_dashboard.png",
        "caption": "Figure 6: Citizen Self-Service Dashboard displaying active ticket summaries, real-time SLA countdowns, and quick-action navigation bars."
    },
    {
        "id": "Figure 7",
        "title": "Active Citizen Grievances Tracker",
        "file": "screenshots/curated/07_citizen_current_grievances.png",
        "caption": "Figure 7: Active Grievances Table showing tracked complaint IDs, assigned municipal departments, priority badges, and lifecycle statuses."
    },
    {
        "id": "Figure 8",
        "title": "Historical Grievance Archive & Feedback Ratings",
        "file": "screenshots/curated/08_citizen_previous_grievances.png",
        "caption": "Figure 8: Historical Grievance Archive allowing citizens to inspect completed resolutions, view closing evidence, and submit 5-star service ratings."
    },
    {
        "id": "Figure 9",
        "title": "Citizen Profile & Communication Settings",
        "file": "screenshots/curated/09_citizen_profile.png",
        "caption": "Figure 9: Citizen Profile Management displaying personal contact details, residential ward assignment, and notification preferences."
    },
    {
        "id": "Figure 10",
        "title": "Multi-Modal Grievance Submission Intake",
        "file": "screenshots/curated/10_citizen_submission_form.png",
        "caption": "Figure 10: Multi-Channel Submission Portal allowing citizens to type natural language grievances, record voice notes, and upload incident photos."
    },
    {
        "id": "Figure 11",
        "title": "Granular Ticket Progress & Real-Time Status Timeline",
        "file": "screenshots/curated/11_citizen_status_tracker.png",
        "caption": "Figure 11: Real-Time Ticket Status Tracker rendering state machine milestones from Submission -> AI Analysis -> Assignment -> Resolution -> Closure."
    },
    {
        "id": "Figure 12",
        "title": "Interactive AI Entity Extraction & Form Review",
        "file": "screenshots/curated/12_citizen_ai_analysis_interactive.png",
        "caption": "Figure 12: Interactive AI Form Review screen showcasing real-time Mistral NLP field extraction, location normalization, and missing field alerts."
    },
    {
        "id": "Figure 13",
        "title": "Complaint Registration Success Confirmation",
        "file": "screenshots/curated/13_complaint_registered_confirmation.png",
        "caption": "Figure 13: Instant Registration Confirmation modal displaying unique Tracking ID, estimated SLA response time, and assigned municipal department."
    },
    {
        "id": "Figure 14",
        "title": "Comprehensive Citizen Grievance Inspection Modal",
        "file": "screenshots/curated/14_citizen_grievance_details_modal.png",
        "caption": "Figure 14: Comprehensive Grievance Details Modal displaying incident metadata, uploaded photographic evidence, officer notes, and audit trails."
    },
    {
        "id": "Figure 15",
        "title": "Nodal Officer Workdesk & Departmental Dashboard",
        "file": "screenshots/curated/15_officer_dashboard.png",
        "caption": "Figure 15: Nodal Officer Operations Dashboard showing assigned queue counts, critical urgency alerts, and SLA deadline monitors."
    },
    {
        "id": "Figure 16",
        "title": "Officer Clarification Requests & Citizen Messaging",
        "file": "screenshots/curated/16_officer_clarifications_tab.png",
        "caption": "Figure 16: Clarification Management Tab enabling officers to request specific follow-up details from complainants without rejecting tickets."
    },
    {
        "id": "Figure 17",
        "title": "Officer Filtered Ticket Queue & Urgency Sorting",
        "file": "screenshots/curated/17_officer_assigned_tickets.png",
        "caption": "Figure 17: Filtered Assigned Tickets View sorted by AI Severity Score, highlighting critical electrical hazards and water contamination tickets."
    },
    {
        "id": "Figure 18",
        "title": "Officer Ticket Inspection & AI Analysis Breakdown",
        "file": "screenshots/curated/18_officer_ticket_details_panel.png",
        "caption": "Figure 18: In-Depth Ticket Details Panel displaying AI Severity Breakdown, extracted location intelligence, and attached citizen evidence."
    },
    {
        "id": "Figure 19",
        "title": "Ticket Lifecycle Action Workflow & Status Progression",
        "file": "screenshots/curated/19_officer_resolve_action_dropdown.png",
        "caption": "Figure 19: Ticket Action Workflow dropdown allowing the nodal officer to advance state from Assigned to In Progress, Inspection, or Resolution."
    },
    {
        "id": "Figure 20",
        "title": "Officer Resolution Submission & Photo Verification Modal",
        "file": "screenshots/curated/20_officer_resolve_ticket_modal.png",
        "caption": "Figure 20: Officer Resolution Modal requiring mandatory upload of 'After' resolution photo evidence and detailed maintenance closure notes."
    },
    {
        "id": "Figure 21",
        "title": "Superadmin Governance & Cross-Departmental Oversight",
        "file": "screenshots/curated/21_admin_dashboard_overview.png",
        "caption": "Figure 21: Superadmin Master Dashboard offering cross-ward heatmaps, jurisdictional workload distributions, and city-wide SLA adherence metrics."
    },
    {
        "id": "Figure 22",
        "title": "Municipal Officer Onboarding & Staff Creation Modal",
        "file": "screenshots/curated/22_admin_add_user_modal.png",
        "caption": "Figure 22: User Creation Modal allowing system administrators to provision new departmental nodal officers and configure role permissions."
    },
    {
        "id": "Figure 23",
        "title": "Inter-Departmental Conflict Adjudication Panel",
        "file": "screenshots/curated/23_admin_conflict_resolution_modal.png",
        "caption": "Figure 23: Conflict Resolution Panel adjudicating inter-departmental boundary disputes (e.g., Road repair vs. Water pipe leakage excavation)."
    },
    {
        "id": "Figure 24",
        "title": "Citizen Feedback & Service Quality Monitoring",
        "file": "screenshots/curated/24_admin_feedback_modal.png",
        "caption": "Figure 24: Citizen Feedback Inspection Modal aggregating citizen satisfaction ratings, sentiment trends, and officer performance audits."
    },
    {
        "id": "Figure 25",
        "title": "Officer Profile & Departmental Jurisdiction Inspector",
        "file": "screenshots/curated/25_admin_user_details_modal.png",
        "caption": "Figure 25: Administrative Staff Details Modal inspecting officer credentials, active assigned caseload, and verified resolution rates."
    },
    {
        "id": "Figure 26",
        "title": "Dynamic Ward & Jurisdictional Boundary Reassignment",
        "file": "screenshots/curated/26_admin_update_jurisdiction_modal.png",
        "caption": "Figure 26: Jurisdiction Reassignment Interface enabling administrators to dynamically reassign wards or departments to balance staff workload."
    }
]

print("Loaded base content definitions.")
