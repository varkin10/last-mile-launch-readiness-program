# Last Mile Launch Readiness Program

**A standardized operating model for launching multiple concurrent Last Mile delivery stations — built as a portfolio case study for Operations Program Manager / Last Mile Launch Manager roles.**

This is not a software project. It's a launch program: a program charter, a standardized launch playbook, cross-functional governance (RACI/RAID), a Day 1 operational validation protocol, Weekly Business Review reporting, and a post-launch continuous-improvement process — applied to 5 simulated station launches. A lightweight Streamlit dashboard sits on top to make the underlying readiness data explorable; it supports the program, it isn't the point of it.

## The Problem

When a logistics company opens multiple Last Mile delivery stations at once, coordination spans nine departments — Operations, HR, Training, Technology, Facilities, Safety, Security, Transportation, and Vendor Management — each running dozens of tasks against a fixed launch date. Tracked in spreadsheets and status meetings, this produces poor visibility, late risk discovery, and inconsistent readiness assessments across sites. There's no standard for what "ready to launch" actually means.

## What This Program Does

1. **Standardizes the launch process** — every site follows the same 9-phase playbook (Site Planning → Facilities → Technology → Hiring → Training → Safety → Operational Testing → Day 1 → Post-Launch Stabilization) with defined entry/exit criteria and quality gates.
2. **Makes readiness measurable** — a readiness score, risk severity score, and launch confidence score are calculated per site from underlying task, milestone, RAID, and validation data — producing a defensible Go/No-Go recommendation instead of a gut call.
3. **Governs cross-functional ownership** — a RACI matrix and RAID log make accountability and risk explicit across all 9 departments plus Finance and Leadership.
4. **Standardizes executive communication** — a Weekly Business Review format keeps leadership focused on program health, top risks, escalations, and decisions needed — not raw task lists.
5. **Closes the loop** — a post-launch retrospective template captures what worked, what failed, and what should be standardized into the next launch.

## Program Artifacts (`/program-artifacts`)

| Artifact | What it is |
|---|---|
| `01_Program_Charter.md` | Business objective, scope, stakeholders, success metrics, risks, operating cadence |
| `02_Launch_Playbook.md` | 9-phase standardized playbook with entry/exit criteria and quality gates |
| `03_04_05_RACI_RAID_Scorecard.xlsx` | RACI matrix, full RAID log, and site readiness scorecard for all 5 sites |
| `06_Executive_WBR_Template.md` | Weekly Business Review format for senior leadership |
| `07_Day1_Readiness_Checklist.md` | Operational validation checklist gating the Go/No-Go decision |
| `08_Post_Launch_Retrospective_Template.md` | Post-launch review and lessons-learned capture |

## Data (`/data`)

Synthetic operational data generated for 5 simulated station launches (`generate_data.py`) — sites, stakeholders, milestones, tasks, RAID items, training, hiring, equipment, Day 1 validation results, budget, schedule variance, and issues. See `docs/data_dictionary.md` for field definitions. Grounded in the structure of public logistics datasets (Amazon Last Mile Routing Research Challenge, Kaggle Amazon Delivery Dataset) for realism, not joined directly since those datasets are route-level rather than launch-program-level.

## Dashboard (`/dashboard`)

A lightweight Streamlit app over the CSV data — Executive Overview, Site Readiness, RAID Log, Milestone Tracker, Stakeholder Ownership, Day 1 Validation, and a WBR Summary page that renders the same content as the WBR document, live.

```bash
cd dashboard
pip install -r requirements.txt
cd ../data && python3 generate_data.py
cd ../dashboard && python3 analytics.py   # generates site_scorecard.csv
streamlit run app.py
```

## The Story

Across the 5 simulated launches, the program surfaces a realistic mix of outcomes as of the current WBR snapshot: 1 site tracking Conditional GO, 4 tracking NO-GO — driven by concentrated technology and operational risk at two sites and schedule slippage at others. That's the point: the value of this operating model isn't that every launch goes perfectly, it's that risk is visible early, ownership is unambiguous, and leadership gets a consistent, comparable readiness picture across every concurrent launch — instead of finding out about a blocker the week of Day 1.

## Folder Structure

```
Last-Mile-Launch-Readiness-Program/
├── program-artifacts/     # Charter, Playbook, RACI/RAID/Scorecard, WBR, Day 1 Checklist, Retrospective
├── data/                  # Synthetic dataset + generator script
├── dashboard/             # Streamlit app + analytics engine
├── docs/                  # Case study, data dictionary, resume/LinkedIn/outreach copy
└── README.md
```
