"""
Last Mile Launch Readiness Program — Analytics Engine
Pure functions over the /data CSVs. Used by app.py (Streamlit) and can be
run standalone / imported into notebooks for the same calculations.
"""
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_all():
    d = {}
    for name in ["sites", "stakeholders", "milestones", "tasks", "raid_log", "raci_matrix",
                 "training", "hiring", "equipment", "day1_validation", "budget",
                 "schedule_variance", "issues"]:
        d[name] = pd.read_csv(os.path.join(DATA_DIR, f"{name}.csv"))
    return d

STATUS_SCORE = {"Complete": 100, "On Track": 80, "At Risk": 50, "Delayed": 30, "Blocked": 10, "Not Started": 0}
SEVERITY_SCORE = {"High": 3, "Medium": 2, "Low": 1}

def department_readiness(tasks_df, site_id=None):
    df = tasks_df if site_id is None else tasks_df[tasks_df.site_id == site_id]
    g = df.groupby("owner_dept")["status"].apply(lambda s: s.map(STATUS_SCORE).mean())
    return g.round(1).rename("readiness_pct")

def site_readiness_score(site_id, tasks_df, milestones_df, raid_df, validation_df):
    t = tasks_df[tasks_df.site_id == site_id]
    task_score = t["status"].map(STATUS_SCORE).mean() if len(t) else 0

    m = milestones_df[milestones_df.site_id == site_id]
    milestone_score = m["status"].map(STATUS_SCORE).mean() if len(m) else 0

    v = validation_df[validation_df.site_id == site_id]
    validation_score = (v["result"].eq("Pass").sum() / len(v) * 100) if len(v) else 0

    r = raid_df[(raid_df.site_id == site_id) & (raid_df.type == "Risk") & (raid_df.status != "Closed")]
    risk_penalty = r["severity"].map(SEVERITY_SCORE).sum() * 1.5  # each open high-severity risk costs 4.5 pts

    raw = 0.40 * task_score + 0.35 * milestone_score + 0.25 * validation_score - risk_penalty
    readiness = max(0, min(100, raw))
    return round(readiness, 1)

def risk_severity_score(raid_df, site_id=None):
    df = raid_df if site_id is None else raid_df[raid_df.site_id == site_id]
    open_risks = df[(df.type == "Risk") & (df.status != "Closed")]
    if len(open_risks) == 0:
        return 0.0
    score = open_risks["severity"].map(SEVERITY_SCORE).sum() / (len(open_risks) * 3) * 100
    return round(score, 1)

def launch_confidence_score(readiness_score, risk_score, schedule_variance_days):
    # Confidence = readiness minus risk drag minus schedule drag, floored at 0
    schedule_penalty = min(20, max(0, schedule_variance_days) * 0.6)
    confidence = readiness_score - (risk_score * 0.15) - schedule_penalty
    return round(max(0, min(100, confidence)), 1)

def go_no_go(confidence_score):
    if confidence_score >= 80:
        return "GO"
    elif confidence_score >= 60:
        return "CONDITIONAL GO"
    else:
        return "NO-GO"

def schedule_variance_total(schedule_variance_df, site_id):
    df = schedule_variance_df[schedule_variance_df.site_id == site_id]
    return int(df["schedule_variance_days"].sum())

def build_site_scorecard():
    d = load_all()
    rows = []
    for _, site in d["sites"].iterrows():
        sid = site["site_id"]
        readiness = site_readiness_score(sid, d["tasks"], d["milestones"], d["raid_log"], d["day1_validation"])
        risk_score = risk_severity_score(d["raid_log"], sid)
        variance = schedule_variance_total(d["schedule_variance"], sid)
        confidence = launch_confidence_score(readiness, risk_score, variance)
        decision = go_no_go(confidence)
        open_blockers = len(d["tasks"][(d["tasks"].site_id == sid) & (d["tasks"].status == "Blocked")])
        critical_risks = len(d["raid_log"][(d["raid_log"].site_id == sid) & (d["raid_log"].type == "Risk") &
                                            (d["raid_log"].severity == "High") & (d["raid_log"].status != "Closed")])
        delayed_milestones = len(d["milestones"][(d["milestones"].site_id == sid) & (d["milestones"].status == "Delayed")])
        rows.append({
            "site_id": sid, "site_name": site["site_name"], "region": site["region"],
            "launch_date": site["launch_date"], "readiness_score": readiness,
            "risk_score": risk_score, "schedule_variance_days": variance,
            "launch_confidence_score": confidence, "go_no_go": decision,
            "open_blockers": open_blockers, "critical_risks": critical_risks,
            "delayed_milestones": delayed_milestones,
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    sc = build_site_scorecard()
    print(sc.to_string(index=False))
    sc.to_csv(os.path.join(DATA_DIR, "site_scorecard.csv"), index=False)
    print("\nSaved data/site_scorecard.csv")
