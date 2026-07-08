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

STATUS_COLORS = {"good": "#2e7d32", "warn": "#f9a825", "bad": "#c62828", "neutral": "#1F3864"}

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }

.dashboard-header {
    background: linear-gradient(135deg, #1F3864 0%, #2E5984 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    color: #FFFFFF;
}
.header-title {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 0.25rem;
}
.header-caption {
    font-size: 0.85rem;
    opacity: 0.9;
}

.page-header {
    margin-bottom: 1rem;
}
.page-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1F3864;
    margin-bottom: 0.15rem;
}
.page-caption {
    font-size: 0.85rem;
    color: #666;
}

.kpi-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.kpi-card {
    flex: 1 1 calc(25% - 0.75rem);
    min-width: 140px;
    background: #FFFFFF;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    border: 1px solid #E8EAED;
}
.kpi-label {
    font-size: 0.75rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1.2;
}

@media (max-width: 768px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
    .dashboard-header { padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; }
    .header-title { font-size: 1.15rem; }
    .header-caption { font-size: 0.75rem; }
    .page-title { font-size: 1.1rem; }
    .page-caption { font-size: 0.75rem; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1rem !important; }
    .kpi-card {
        flex: 1 1 calc(50% - 0.75rem);
        min-width: unset;
        padding: 0.75rem 1rem;
    }
    .kpi-value { font-size: 1.3rem; }
    .kpi-label { font-size: 0.65rem; }
}
</style>
""", unsafe_allow_html=True)


def score_status(val, good=80, warn=65):
    if val >= good:
        return "good"
    if val >= warn:
        return "warn"
    return "bad"


def gongo_status(val):
    return {"GO": "good", "CONDITIONAL GO": "warn", "NO-GO": "bad"}.get(val, "neutral")


def kpi_row(kpis):
    cards = []
    for kpi in kpis:
        status = kpi.get("status", "neutral")
        color = STATUS_COLORS.get(status, STATUS_COLORS["neutral"])
        cards.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{kpi["label"]}</div>'
            f'<div class="kpi-value" style="color: {color};">{kpi["value"]}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="kpi-row">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_banner(title, caption=None):
    cap_html = f'<div class="header-caption">{caption}</div>' if caption else ""
    st.markdown(
        f'<div class="dashboard-header">'
        f'<div class="header-title">{title}</div>{cap_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_page_header(title, caption=None):
    cap_html = f'<div class="page-caption">{caption}</div>' if caption else ""
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">{title}</div>{cap_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


@st.cache_data
def get_data():
    d = load_all()
    d["scorecard"] = build_site_scorecard()
    return d

d = get_data()
sites, tasks, milestones, raid, validation = d["sites"], d["tasks"], d["milestones"], d["raid_log"], d["day1_validation"]
scorecard = d["scorecard"]

GONOGO_COLOR = {"GO": "#2e7d32", "CONDITIONAL GO": "#f9a825", "NO-GO": "#c62828"}

PAGES = [
    "Executive Overview", "Site Readiness", "RAID Log", "Milestone Tracker",
    "Stakeholder Ownership", "Day 1 Validation", "WBR Summary",
]

with st.sidebar:
    st.caption("Navigation is at the top of the page.")
    st.divider()
    st.caption("Data: synthetic operational dataset generated for this case study. See /data and data_dictionary.md.")

page = st.selectbox("Navigate", PAGES, label_visibility="collapsed")

render_banner(
    "📦 Last Mile Launch Readiness Program",
    "5 simulated station launches · Program snapshot: August 2026",
)

# ---------------------------------------------------------------- EXECUTIVE OVERVIEW
if page == "Executive Overview":
    render_page_header("Executive Launch Dashboard", "Program-level readiness across all 5 concurrent station launches")

    healthy_sites = (scorecard.go_no_go != "NO-GO").sum()
    critical_risks = int(scorecard["critical_risks"].sum())
    kpi_row([
        {"label": "Avg Readiness Score", "value": f"{scorecard['readiness_score'].mean():.1f}",
         "status": score_status(scorecard["readiness_score"].mean())},
        {"label": "Avg Launch Confidence", "value": f"{scorecard['launch_confidence_score'].mean():.1f}",
         "status": score_status(scorecard["launch_confidence_score"].mean())},
        {"label": "Sites GO / Conditional", "value": f"{healthy_sites} of {len(scorecard)}",
         "status": "good" if healthy_sites == len(scorecard) else "warn" if healthy_sites > 0 else "bad"},
        {"label": "Open Critical Risks", "value": str(critical_risks),
         "status": "good" if critical_risks == 0 else "warn" if critical_risks <= 3 else "bad"},
    ])

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
    render_page_header("Site Readiness")
    site_pick = st.selectbox("Select site", sites["site_name"])
    site_id = sites[sites.site_name == site_pick]["site_id"].values[0]
    row = scorecard[scorecard.site_id == site_id].iloc[0]
    variance = row["schedule_variance_days"]

    kpi_row([
        {"label": "Readiness Score", "value": str(row["readiness_score"]),
         "status": score_status(row["readiness_score"])},
        {"label": "Confidence Score", "value": str(row["launch_confidence_score"]),
         "status": score_status(row["launch_confidence_score"])},
        {"label": "Go/No-Go", "value": row["go_no_go"], "status": gongo_status(row["go_no_go"])},
        {"label": "Schedule Variance", "value": f"{variance} days",
         "status": "good" if variance <= 0 else "warn" if variance <= 3 else "bad"},
    ])

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
    render_page_header("RAID Log — Risks, Assumptions, Issues, Dependencies")
    c1, c2 = st.columns(2)
    type_filter = c1.multiselect("Type", raid.type.unique(), default=list(raid.type.unique()))
    site_filter = c2.multiselect("Site", raid.site_id.unique(), default=list(raid.site_id.unique()))
    filtered = raid[raid.type.isin(type_filter) & raid.site_id.isin(site_filter)]

    open_count = len(filtered[filtered.status.isin(["Open", "Escalated"])])
    high_sev = len(filtered[(filtered.severity == "High") & (filtered.status != "Closed")])
    kpi_row([
        {"label": "Total Items", "value": str(len(filtered)), "status": "neutral"},
        {"label": "Open", "value": str(open_count),
         "status": "good" if open_count == 0 else "warn" if open_count <= 5 else "bad"},
        {"label": "High Severity Open", "value": str(high_sev),
         "status": "good" if high_sev == 0 else "bad"},
    ])

    fig = px.sunburst(filtered, path=["type", "category", "severity"], title="RAID Breakdown")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- MILESTONE TRACKER
elif page == "Milestone Tracker":
    render_page_header("Milestone Tracker")
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
    render_page_header("Cross-Functional Stakeholder Ownership")
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
    render_page_header("Day 1 Operational Validation")
    site_pick = st.selectbox("Select site", sites["site_name"], key="val_site")
    site_id = sites[sites.site_name == site_pick]["site_id"].values[0]
    v = validation[validation.site_id == site_id]

    pass_rate = (v.result == "Pass").mean() * 100
    kpi_row([
        {"label": "Validation Pass Rate", "value": f"{pass_rate:.0f}%",
         "status": "good" if pass_rate >= 90 else "warn" if pass_rate >= 75 else "bad"},
    ])
    fig = px.bar(v, x="checklist_item", y=[1]*len(v), color="result",
                 color_discrete_map={"Pass": "#2e7d32", "Fail": "#c62828", "Pending": "#f9a825"},
                 title=f"Day 1 Checklist — {site_pick}")
    fig.update_yaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(v, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- WBR SUMMARY
elif page == "WBR Summary":
    render_page_header(
        "Weekly Business Review — Auto-Generated Summary",
        "This page renders the same content that goes into the Executive WBR document, pulled live from current data.",
    )

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
