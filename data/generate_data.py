"""
Last Mile Launch Readiness Program — Synthetic Data Generator
Generates realistic operational data for 5 simulated delivery station launches.
Run: python3 generate_data.py
Outputs CSVs into this /data folder.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# "As of" snapshot date for this case study — the dashboard tells the story
# as if the program is being reviewed on this date. Sites launching later
# will naturally show less progress, which mirrors a real multi-site rollout.
AS_OF = datetime(2026, 8, 5)

SITES = [
    {"site_id": "DXP1", "site_name": "Columbus East", "region": "Midwest", "launch_date": "2026-08-17", "site_type": "Same-Day"},
    {"site_id": "DXP2", "site_name": "Charlotte South", "region": "Southeast", "launch_date": "2026-09-01", "site_type": "Standard"},
    {"site_id": "DXP3", "site_name": "Phoenix West", "region": "Southwest", "launch_date": "2026-09-14", "site_type": "Standard"},
    {"site_id": "DXP4", "site_name": "Newark Metro", "region": "Northeast", "launch_date": "2026-08-24", "site_type": "Same-Day"},
    {"site_id": "DXP5", "site_name": "Denver North", "region": "Mountain West", "launch_date": "2026-09-28", "site_type": "Standard"},
]
sites_df = pd.DataFrame(SITES)
sites_df.to_csv("sites.csv", index=False)

DEPARTMENTS = ["Operations", "HR", "Training", "Technology", "Facilities",
               "Safety", "Security", "Transportation", "Vendor Readiness"]

STAKEHOLDERS = [
    {"stakeholder_id": "S01", "name": "Launch Manager", "department": "Program", "role": "Launch Manager", "raci_default": "A"},
    {"stakeholder_id": "S02", "name": "Site Leader", "department": "Operations", "role": "Site Leader", "raci_default": "R"},
    {"stakeholder_id": "S03", "name": "Ops Manager", "department": "Operations", "role": "Operations Manager", "raci_default": "R"},
    {"stakeholder_id": "S04", "name": "HR Business Partner", "department": "HR", "role": "HR Lead", "raci_default": "R"},
    {"stakeholder_id": "S05", "name": "Training Lead", "department": "Training", "role": "Training Lead", "raci_default": "R"},
    {"stakeholder_id": "S06", "name": "IT Site Engineer", "department": "Technology", "role": "IT Lead", "raci_default": "R"},
    {"stakeholder_id": "S07", "name": "Facilities Manager", "department": "Facilities", "role": "Facilities Lead", "raci_default": "R"},
    {"stakeholder_id": "S08", "name": "Safety Manager", "department": "Safety", "role": "Safety Lead", "raci_default": "R"},
    {"stakeholder_id": "S09", "name": "Security Lead", "department": "Security", "role": "Security Lead", "raci_default": "C"},
    {"stakeholder_id": "S10", "name": "Transportation Manager", "department": "Transportation", "role": "Transportation Lead", "raci_default": "R"},
    {"stakeholder_id": "S11", "name": "Finance Partner", "department": "Finance", "role": "Finance Business Partner", "raci_default": "C"},
    {"stakeholder_id": "S12", "name": "Vendor Manager", "department": "Vendor Management", "role": "Procurement/Vendor Lead", "raci_default": "R"},
    {"stakeholder_id": "S13", "name": "Regional Ops Director", "department": "Leadership", "role": "Regional Director", "raci_default": "I"},
]
stakeholders_df = pd.DataFrame(STAKEHOLDERS)
stakeholders_df.to_csv("stakeholders.csv", index=False)

PHASES = ["Site Planning", "Facilities Readiness", "Technology Readiness", "Hiring Readiness",
          "Training Readiness", "Safety Validation", "Operational Testing", "Day 1 Launch",
          "Post-Launch Stabilization"]

TASK_LIBRARY = {
    "Site Planning": ["Finalize site layout", "Confirm lease/permits", "Approve headcount plan", "Publish launch schedule"],
    "Facilities Readiness": ["Complete build-out", "Install racking/conveyor", "Fire inspection sign-off", "Dock leveler install"],
    "Technology Readiness": ["Network/WiFi install", "Scanner provisioning", "WMS go-live config", "Badge access system live"],
    "Hiring Readiness": ["Post job requisitions", "Complete hiring events", "Background checks cleared", "Offer acceptance target met"],
    "Training Readiness": ["Trainer certification", "New hire orientation scheduled", "SOP training completed", "Safety training completed"],
    "Safety Validation": ["Safety audit passed", "PPE stock confirmed", "Emergency evacuation plan posted", "Incident escalation tested"],
    "Operational Testing": ["Scanner load test", "Route staging dry run", "Dock throughput test", "Peak volume simulation"],
    "Day 1 Launch": ["Leadership sign-off obtained", "Day 1 staffing confirmed", "Go/No-Go review completed", "Launch war room staffed"],
    "Post-Launch Stabilization": ["Daily stand-ups (Week 1)", "Defect/issue log review", "30-day performance review", "Lessons learned session"],
}

DEPT_BY_PHASE = {
    "Site Planning": "Operations", "Facilities Readiness": "Facilities", "Technology Readiness": "Technology",
    "Hiring Readiness": "HR", "Training Readiness": "Training", "Safety Validation": "Safety",
    "Operational Testing": "Operations", "Day 1 Launch": "Operations", "Post-Launch Stabilization": "Operations",
}

STATUS_WEIGHTS = {"Complete": 0.45, "On Track": 0.25, "At Risk": 0.18, "Delayed": 0.08, "Blocked": 0.04}

def weighted_status():
    return np.random.choice(list(STATUS_WEIGHTS.keys()), p=list(STATUS_WEIGHTS.values()))

milestones, tasks = [], []
mid, tid = 1, 1
for site in SITES:
    launch = datetime.strptime(site["launch_date"], "%Y-%m-%d")
    phase_start = launch - timedelta(days=120)
    for i, phase in enumerate(PHASES):
        phase_end = phase_start + timedelta(days=12)
        status = weighted_status() if phase_end < AS_OF else "Not Started"
        if phase == "Day 1 Launch" and phase_end < AS_OF + timedelta(days=20):
            status = "On Track" if site["site_id"] != "DXP3" else "At Risk"
        milestones.append({
            "milestone_id": f"M{mid:03d}", "site_id": site["site_id"], "phase": phase,
            "planned_date": phase_end.strftime("%Y-%m-%d"), "owner_dept": DEPT_BY_PHASE[phase],
            "status": status, "sequence": i + 1,
        })
        for t in TASK_LIBRARY[phase]:
            tstatus = weighted_status() if phase_end < AS_OF else "Not Started"
            tasks.append({
                "task_id": f"T{tid:04d}", "site_id": site["site_id"], "phase": phase,
                "task_name": t, "owner_dept": DEPT_BY_PHASE[phase],
                "due_date": (phase_end - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d"),
                "status": tstatus,
                "priority": random.choice(["High", "Medium", "Low"]),
            })
            tid += 1
        mid += 1
        phase_start = phase_end

pd.DataFrame(milestones).to_csv("milestones.csv", index=False)
pd.DataFrame(tasks).to_csv("tasks.csv", index=False)

RISK_CATEGORIES = ["Schedule", "Operational", "People", "Technology", "Facilities", "Vendor"]
raid_rows = []
rid = 1
raid_templates = [
    ("Risk", "Scanner devices delayed from vendor shipment", "Technology", "High", "Medium"),
    ("Risk", "Hiring pipeline below target for launch date", "People", "High", "High"),
    ("Risk", "Dock leveler installation behind schedule", "Facilities", "Medium", "Medium"),
    ("Risk", "WiFi coverage gaps in mezzanine area", "Technology", "Medium", "Low"),
    ("Issue", "Fire inspection failed on first attempt", "Facilities", "High", "High"),
    ("Issue", "Background check turnaround exceeding SLA", "People", "Medium", "Medium"),
    ("Issue", "Badge access system misconfigured for contractors", "Technology", "Medium", "Low"),
    ("Assumption", "Regional labor market will support hiring plan", "People", "Medium", "Medium"),
    ("Assumption", "Vendor delivers racking on committed date", "Vendor", "Medium", "Medium"),
    ("Dependency", "WMS go-live depends on network install completion", "Technology", "High", "High"),
    ("Dependency", "Day 1 staffing depends on training completion", "People", "High", "High"),
    ("Dependency", "Route staging test depends on dock readiness", "Operational", "Medium", "Medium"),
    ("Risk", "Peak season volume may exceed site design capacity", "Operational", "High", "Medium"),
    ("Issue", "Safety audit found missing PPE inventory", "Safety", "Medium", "Low"),
    ("Risk", "Transportation route conflicts with neighboring site", "Operational", "Low", "Medium"),
]
OWNERS = ["Site Leader", "Ops Manager", "IT Lead", "HR Lead", "Facilities Lead", "Safety Lead", "Vendor Manager", "Training Lead"]
STATUS_RAID = ["Open", "Open", "Mitigating", "Closed", "Escalated"]

for site in SITES:
    n = random.randint(3, 5)
    picks = random.sample(raid_templates, n)
    for kind, desc, cat, sev, prob in picks:
        raid_rows.append({
            "raid_id": f"R{rid:03d}", "site_id": site["site_id"], "type": kind,
            "description": desc, "category": cat, "severity": sev, "probability": prob,
            "owner": random.choice(OWNERS),
            "mitigation": "Escalate to vendor / accelerate parallel workstream / add contingency buffer",
            "due_date": (datetime.strptime(site["launch_date"], "%Y-%m-%d") - timedelta(days=random.randint(5, 45))).strftime("%Y-%m-%d"),
            "status": random.choice(STATUS_RAID),
        })
        rid += 1
pd.DataFrame(raid_rows).to_csv("raid_log.csv", index=False)

# RACI matrix: activities x stakeholders
raci_activities = [
    "Site Selection & Lease Approval", "Facilities Build-Out", "Network & Technology Install",
    "Hiring Plan & Recruiting", "New Hire Training", "Safety Audit & Certification",
    "Operational Readiness Testing", "Go/No-Go Decision", "Day 1 Launch Execution",
    "Post-Launch Stabilization", "Budget & Financial Tracking", "Vendor Delivery Management",
]
raci_roles = ["Launch Manager", "Site Leader", "Operations Manager", "HR Lead", "Training Lead",
              "IT Lead", "Facilities Lead", "Safety Lead", "Security Lead", "Transportation Lead",
              "Finance Partner", "Vendor Manager"]

raci_matrix = {
    "Site Selection & Lease Approval":      {"Launch Manager":"A","Site Leader":"C","Operations Manager":"C","Finance Partner":"C","Facilities Lead":"R"},
    "Facilities Build-Out":                 {"Launch Manager":"A","Facilities Lead":"R","Vendor Manager":"R","Safety Lead":"C","Site Leader":"I"},
    "Network & Technology Install":         {"Launch Manager":"A","IT Lead":"R","Vendor Manager":"C","Site Leader":"I"},
    "Hiring Plan & Recruiting":             {"Launch Manager":"A","HR Lead":"R","Site Leader":"C","Operations Manager":"C"},
    "New Hire Training":                    {"Launch Manager":"I","Training Lead":"R","HR Lead":"C","Site Leader":"A"},
    "Safety Audit & Certification":         {"Launch Manager":"I","Safety Lead":"R","Facilities Lead":"C","Site Leader":"A"},
    "Operational Readiness Testing":        {"Launch Manager":"A","Operations Manager":"R","IT Lead":"C","Site Leader":"R"},
    "Go/No-Go Decision":                    {"Launch Manager":"A","Site Leader":"R","Operations Manager":"C","Safety Lead":"C","Security Lead":"C"},
    "Day 1 Launch Execution":               {"Launch Manager":"A","Site Leader":"R","Operations Manager":"R","Transportation Lead":"R"},
    "Post-Launch Stabilization":            {"Launch Manager":"A","Site Leader":"R","Operations Manager":"R","Training Lead":"C"},
    "Budget & Financial Tracking":          {"Launch Manager":"A","Finance Partner":"R","Site Leader":"I"},
    "Vendor Delivery Management":           {"Launch Manager":"C","Vendor Manager":"R","Facilities Lead":"C","IT Lead":"C"},
}
raci_rows = []
for activity in raci_activities:
    row = {"Activity": activity}
    for role in raci_roles:
        row[role] = raci_matrix[activity].get(role, "")
    raci_rows.append(row)
pd.DataFrame(raci_rows).to_csv("raci_matrix.csv", index=False)

# Training / Hiring / Equipment / Validation / Budget / Schedule Variance / Issues
training_rows, hiring_rows, equip_rows, validation_rows, budget_rows, variance_rows, issue_rows = [],[],[],[],[],[],[]
tr_id = eq_id = va_id = bg_id = sv_id = is_id = 1
VALIDATION_ITEMS = ["Badge Access", "Scanner/Device Testing", "WiFi/Network Validation", "Dock Readiness",
                     "Route Staging", "Associate Onboarding Check", "Training Completion", "Safety Audit",
                     "Parking/Staging Area", "Incident Escalation Process", "Leadership Signoff"]

for site in SITES:
    launch = datetime.strptime(site["launch_date"], "%Y-%m-%d")
    training_rows.append({
        "site_id": site["site_id"], "planned_associates": random.randint(180, 260),
        "trained_associates": random.randint(120, 250),
        "trainer_certifications_complete": random.choice([True, True, False]),
        "training_completion_pct": round(random.uniform(60, 100), 1),
    })
    hiring_rows.append({
        "site_id": site["site_id"], "headcount_target": random.randint(180, 260),
        "offers_extended": random.randint(150, 260), "offers_accepted": random.randint(120, 240),
        "background_checks_cleared": random.randint(100, 230),
        "hiring_completion_pct": round(random.uniform(55, 100), 1),
    })
    for eq in ["Handheld Scanners", "Dock Doors", "Conveyor Belts", "WiFi Access Points", "Badge Readers"]:
        equip_rows.append({
            "equipment_id": f"E{eq_id:03d}", "site_id": site["site_id"], "equipment_type": eq,
            "quantity_planned": random.randint(10, 60), "quantity_installed": random.randint(5, 60),
            "status": random.choice(["Installed", "Installed", "In Progress", "Delayed"]),
        })
        eq_id += 1
    for item in VALIDATION_ITEMS:
        result = random.choices(["Pass", "Fail", "Pending"], weights=[0.65, 0.15, 0.20])[0]
        validation_rows.append({
            "validation_id": f"V{va_id:03d}", "site_id": site["site_id"], "checklist_item": item,
            "result": result, "owner": random.choice(OWNERS),
            "checked_date": (launch - timedelta(days=random.randint(1, 20))).strftime("%Y-%m-%d"),
            "comments": "" if result == "Pass" else "Remediation in progress",
        })
        va_id += 1
    planned = random.randint(1_200_000, 2_400_000)
    actual = int(planned * random.uniform(0.85, 1.18))
    budget_rows.append({
        "site_id": site["site_id"], "budget_category": "Total Launch Budget",
        "planned_cost_usd": planned, "actual_cost_usd": actual,
        "variance_usd": actual - planned, "variance_pct": round((actual - planned) / planned * 100, 1),
    })
    for phase in PHASES:
        planned_days = random.randint(10, 16)
        actual_days = planned_days + random.randint(-3, 3)
        variance_rows.append({
            "site_id": site["site_id"], "phase": phase,
            "planned_duration_days": planned_days, "actual_duration_days": actual_days,
            "schedule_variance_days": actual_days - planned_days,
        })
    for _ in range(random.randint(2, 4)):
        issue_rows.append({
            "issue_id": f"I{is_id:03d}", "site_id": site["site_id"],
            "issue": random.choice(["Late equipment delivery", "Staffing shortfall", "Training bottleneck",
                                     "Permit delay", "Network outage during testing", "Vendor no-show"]),
            "department": random.choice(DEPARTMENTS),
            "resolution_status": random.choice(["Resolved", "In Progress", "Resolved", "Escalated"]),
            "days_to_resolve": random.randint(1, 14),
        })
        is_id += 1

pd.DataFrame(training_rows).to_csv("training.csv", index=False)
pd.DataFrame(hiring_rows).to_csv("hiring.csv", index=False)
pd.DataFrame(equip_rows).to_csv("equipment.csv", index=False)
pd.DataFrame(validation_rows).to_csv("day1_validation.csv", index=False)
pd.DataFrame(budget_rows).to_csv("budget.csv", index=False)
pd.DataFrame(variance_rows).to_csv("schedule_variance.csv", index=False)
pd.DataFrame(issue_rows).to_csv("issues.csv", index=False)

print("All datasets generated in /data")
for f in ["sites","stakeholders","milestones","tasks","raid_log","raci_matrix","training",
          "hiring","equipment","day1_validation","budget","schedule_variance","issues"]:
    df = pd.read_csv(f"{f}.csv")
    print(f"{f}.csv -> {len(df)} rows")
