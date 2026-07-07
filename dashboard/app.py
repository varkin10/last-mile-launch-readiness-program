"""
Last Mile Launch Readiness Program — Operations Dashboard
Streamlit app supporting the program case study. This is a lightweight
analytics layer over the /data CSVs — the program artifacts (charter,
playbook, RACI, RAID, WBR) are the primary deliverables; this dashboard
makes the underlying data explorable.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import load_all, build_site_scorecard, department_readiness

st.set_page_config(page_title="Last Mile Launch Readiness Program", layout="wide", page_icon="📦",
                    initial_sidebar_state="collapsed")

# Mobile-friendly tweaks: tighter padding, smaller metric font, wrap tables
st.markdown("""
<style>
@media (max-width: 768px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 2rem; }
    [data-testid="stMetricValue"] { font-size: 1.4rem; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; }
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1.05rem !important; }
}
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    d = load_all()
    d["scorecard"] = build_site_scorecard()
    return d

d = get_data()
sites, tasks, milestones, raid, validation = d["sites"], d["tasks"], d["milestones"], d["raid_log"], d["day1_validation"]
scorecard = d["scorecard"]

GONOGO_COLOR = {"GO": "#2e7d32", "CONDITIONAL GO": "#f9a825", "NO-GO": "#c62828"}

st.sidebar.title("📦 LAST MILE LAUNCH\nREADINESS PROGRAM")
st.sidebar.caption("5 simulated station launches | Program snapshot: Aug 2026")
page = st.sidebar.radio("Navigate", [
    "Executive Overview", "Site Readiness", "RAID Log", "Milestone Tracker",
    "Stakeholder Ownership", "Day 1 Validation", "WBR Summary",
])
st.sidebar.divider()
st.sidebar.caption("Data: synthetic operational dataset generated for this case study. See /data and data_dictionary.md.")

# ---------------------------------------------------------------- EXECUTIVE OVERVIEW
if page == "Executive Overview":
    st.title("Executive Launch Dashboard")
    st.caption("Program-level readiness across all 5 concurrent station launches")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Readiness Score", f"{scorecard['readiness_score'].mean():.1f}")
    c2.metric("Avg Launch Confidence", f"{scorecard['launch_confidence_score'].mean():.1f}")
    c3.metric("Sites GO / Conditional", f"{(scorecard.go_no_go != 'NO-GO').sum()} of {len(scorecard)}")
    c4.metric("Open Critical Risks", int(scorecard["critical_risks"].sum()))

    st.divider()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(scorecard.sort_values("launch_confidence_score"), x="launch_confidence_score", y="site_name",
                     orientation="h", color="go_no_go", color_discrete_map=GONOGO_COLOR,
                     title="Launch Confidence Score by Site", labels={"launch_confidence_score": "Confidence Score", "site_name": ""})
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        counts = scorecard["go_no_go"].value_counts().reset_index()
        counts.columns = ["decision", "count"]
        fig2 = px.pie(counts, names="decision", values="count", color="decision",
                      color_discrete_map=GONOGO_COLOR, title="Go/No-Go Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Site Readiness Scorecard")
    display = scorecard[["site_name", "region", "launch_date", "readiness_score", "risk_score",
                          "schedule_variance_days", "launch_confidence_score", "go_no_go",
                          "open_blockers", "critical_risks", "delayed_milestones"]]
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Top Program Risks")
    top_risks = raid[(raid.type == "Risk") & (raid.status != "Closed")].sort_values("severity")
    st.dataframe(top_risks[["site_id", "description", "severity", "probability", "owner", "status", "due_date"]],
                 use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- SITE READINESS
elif page == "Site Readiness":
    st.title("Site Readiness")
    site_pick = st.selectbox("Select site", sites["site_name"])
    site_id = sites[sites.site_name == site_pick]["site_id"].values[0]
    row = scorecard[scorecard.site_id == site_id].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Readiness Score", row["readiness_score"])
    c2.metric("Confidence Score", row["launch_confidence_score"])
    c3.metric("Go/No-Go", row["go_no_go"])
    c4.metric("Schedule Variance", f"{row['schedule_variance_days']} days")

    st.divider()
    dept_read = department_readiness(tasks, site_id).reset_index()
    fig = px.bar(dept_read, x="readiness_pct", y="owner_dept", orientation="h",
                 title=f"Department Readiness — {site_pick}", labels={"readiness_pct": "Readiness %", "owner_dept": "Department"},
                 range_x=[0, 100], color="readiness_pct", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Open Risks & Issues for this Site")
    site_raid = raid[raid.site_id == site_id]
    st.dataframe(site_raid, use_container_width=True, hide_index=True)

    st.subheader("Task Detail")
    site_tasks = tasks[tasks.site_id == site_id]
    status_filter = st.multiselect("Filter by status", site_tasks.status.unique(), default=list(site_tasks.status.unique()))
    st.dataframe(site_tasks[site_tasks.status.isin(status_filter)], use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- RAID LOG
elif page == "RAID Log":
    st.title("RAID Log — Risks, Assumptions, Issues, Dependencies")
    c1, c2 = st.columns(2)
    type_filter = c1.multiselect("Type", raid.type.unique(), default=list(raid.type.unique()))
    site_filter = c2.multiselect("Site", raid.site_id.unique(), default=list(raid.site_id.unique()))
    filtered = raid[raid.type.isin(type_filter) & raid.site_id.isin(site_filter)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Items", len(filtered))
    c2.metric("Open", len(filtered[filtered.status.isin(["Open", "Escalated"])]))
    c3.metric("High Severity Open", len(filtered[(filtered.severity == "High") & (filtered.status != "Closed")]))

    fig = px.sunburst(filtered, path=["type", "category", "severity"], title="RAID Breakdown")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- MILESTONE TRACKER
elif page == "Milestone Tracker":
    st.title("Milestone Tracker")
    fig = px.timeline(milestones, x_start="planned_date", x_end="planned_date", y="site_id",
                       color="status", title="Milestone Timeline by Site")
    fig2 = px.scatter(milestones, x="planned_date", y="site_id", color="status", symbol="phase",
                       title="Milestones by Planned Date", size_max=10)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Delayed / Blocked Milestones")
    problem = milestones[milestones.status.isin(["Delayed", "Blocked", "At Risk"])]
    st.dataframe(problem, use_container_width=True, hide_index=True)

    st.subheader("All Milestones")
    st.dataframe(milestones, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- STAKEHOLDER OWNERSHIP
elif page == "Stakeholder Ownership":
    st.title("Cross-Functional Stakeholder Ownership")
    workload = tasks.groupby("owner_dept").agg(total_tasks=("task_id", "count"),
                                                 blocked=("status", lambda s: (s == "Blocked").sum()),
                                                 delayed=("status", lambda s: (s == "Delayed").sum())).reset_index()
    fig = px.bar(workload, x="owner_dept", y="total_tasks", title="Task Ownership by Department")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Overdue / At-Risk Actions by Department")
    st.dataframe(workload.sort_values("blocked", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("RACI Matrix")
    raci = pd.read_csv("../data/raci_matrix.csv")
    st.dataframe(raci, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- DAY 1 VALIDATION
elif page == "Day 1 Validation":
    st.title("Day 1 Operational Validation")
    site_pick = st.selectbox("Select site", sites["site_name"], key="val_site")
    site_id = sites[sites.site_name == site_pick]["site_id"].values[0]
    v = validation[validation.site_id == site_id]

    pass_rate = (v.result == "Pass").mean() * 100
    st.metric("Validation Pass Rate", f"{pass_rate:.0f}%")
    fig = px.bar(v, x="checklist_item", y=[1]*len(v), color="result",
                 color_discrete_map={"Pass": "#2e7d32", "Fail": "#c62828", "Pending": "#f9a825"},
                 title=f"Day 1 Checklist — {site_pick}")
    fig.update_yaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(v, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- WBR SUMMARY
elif page == "WBR Summary":
    st.title("Weekly Business Review — Auto-Generated Summary")
    st.caption("This page renders the same content that goes into the Executive WBR document, pulled live from current data.")

    healthy = (scorecard.go_no_go != "NO-GO").sum()
    st.markdown(f"### Program Health: {'🟢 Green' if healthy == len(scorecard) else '🟡 Yellow' if healthy > 0 else '🔴 Red'}")
    st.markdown(f"**{healthy} of {len(scorecard)} sites** tracking GO or Conditional GO this week.")

    st.subheader("Site-by-Site Readiness")
    st.dataframe(scorecard[["site_name", "region", "launch_date", "readiness_score",
                             "launch_confidence_score", "go_no_go"]], use_container_width=True, hide_index=True)

    st.subheader("Top Risks")
    top = raid[(raid.type == "Risk") & (raid.status != "Closed")].sort_values("severity").head(5)
    for _, r in top.iterrows():
        st.markdown(f"- **[{r.site_id}]** {r.description} — *Owner: {r.owner}, Severity: {r.severity}, Due: {r.due_date}*")

    st.subheader("Escalations")
    esc = raid[raid.status == "Escalated"]
    if len(esc):
        for _, r in esc.iterrows():
            st.markdown(f"- **[{r.site_id}]** {r.description} — needs leadership decision by {r.due_date}")
    else:
        st.markdown("_No open escalations this week._")

    st.subheader("Next 7-Day Priorities")
    upcoming = milestones[milestones.status == "Not Started"].sort_values("planned_date").head(7)
    st.dataframe(upcoming[["site_id", "phase", "planned_date", "owner_dept"]], use_container_width=True, hide_index=True)
