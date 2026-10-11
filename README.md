# MoveInSync Employee App: Play Store Rating Turnaround & Reliability Blueprint

[![Python 3.11](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Telemetry Automation](https://img.shields.io/badge/Telemetry-Ratings%20Pulse%20(Automated)-success.svg)](#continuous-monitoring-ratings-pulse)
[![Target App](https://img.shields.io/badge/Android%20Target-com.moveinsync.ets-brightgreen.svg)](https://play.google.com/store/apps/details?id=com.moveinsync.ets)
[![Assignment](https://img.shields.io/badge/Role-Forward%20Deployed%20Engineer%20(Intern%20to%20FTE)-orange.svg)](#)

> **Prepared by:** Ankur Choudhary  
> **Role:** Forward Deployed Engineer (Intern to FTE) Candidate Assignment  
> **Target:** Elevating MoveInSync's Play Store ratings from a volatile **4.3★** to a durable **4.6+★** across **115,000+** lifetime reviews.

---

## 🎯 Executive Summary & Core Thesis

MoveInSync powers daily commutes for **1.5M+ employees across 430+ marquee enterprise clients**. While B2B client retention remains stellar, its employee-facing Android app (`com.moveinsync.ets`) fluctuates around **4.3★**. 

### The Core Systems Thesis:
MoveInSync's Play Store rating is **not primarily a cosmetic UI problem**. The employee mobile app is the only visible digital surface of an interdependent physical ecosystem spanning drivers, fleet vendors, dynamic routing engines, employer HR rosters, client transport desks, and payroll deduction rules.

When a physical cab is late, when GPS drops, or when a driver erroneously marks a no-show, the employee has no control, cannot switch apps, cannot see who is accountable, and fears financial or disciplinary penalties. The Play Store review box becomes their sole escalation channel. The shared sentiment across hundreds of public reviews is:  
> *"The system is wrong about me, and I have no power to fix it."*

The rating is therefore a lagging indicator of **commute reliability, perceived fairness, and recovery speed**.

---

## 📊 The Mathematical Reality: Arithmetic of Recovery

Any candidate who promises to *"raise the lifetime rating from 4.3★ to 4.7★ in 90 days"* does not understand data. 

If Google Play calculated a pure arithmetic lifetime average, the number of consecutive net-new 5-star reviews ($x$) required to raise a rating from current average $r$ to target average $t$ over a lifetime base of $N$ ratings is governed by:

$$x = \frac{N \cdot (t - r)}{5 - t}$$

For MoveInSync, where $N \approx 115,000$ and $r = 4.3$:
- **To reach 4.4★:** Requires $x \approx \mathbf{19,166}$ pure 5-star reviews.
- **To reach 4.5★:** Requires $x \approx \mathbf{46,000}$ pure 5-star reviews.
- **To reach 4.6★:** Requires $x \approx \mathbf{86,250}$ pure 5-star reviews.
- **To reach 4.7★:** Requires $x \approx \mathbf{153,333}$ pure 5-star reviews (assuming zero 1-star reviews)!

### Strategic Implication:
Because Google Play weights newer ratings more heavily, executive reporting must focus on **Trailing 30-Day Average Rating**, **Weekly 1-Star Review Share**, and leading operational metrics rather than noisy lifetime averages.

---

## 🏗️ Repository Architecture & Codebase

This repository contains production-ready proof-of-concept implementations for the automated tools and backend guardrails proposed in the case study:

```
moveinsync-fde-turnaround/
├── README.md                                  # Executive repository guide & architecture
├── docs/
│   └── MoveInSync_FDE_PlayStore_Turnaround_Case_Study.pdf # Master 12-page PDF submission
├── ratings_pulse/
│   ├── ratings_pulse.py                       # Automated Play Store scraper & regex NLP engine
│   └── pulse_out/pulse.md                     # Generated weekly executive markdown digest
├── services/
│   ├── no_show_fairness_engine.py             # Geofence & dwell verification + 1-tap auto-reversal
│   └── idempotent_booking_api.py              # Idempotent booking API + transactional outbox
├── dashboard/
│   └── index.html                             # Interactive Executive Dashboard & Simulator
└── .github/
    └── workflows/ratings_pulse.yml            # Weekly GitHub Actions cron job (Mondays 08:30 IST)
```

---

## 🛠️ Proof-of-Concept Implementations

### 1. Automated Telemetry Engine (`ratings_pulse/ratings_pulse.py`)
Answers the executive question: *"How are our Play Store ratings?"* in a single 30-second repeatable command.
- Scrapes reviews via `google-play-scraper`.
- Classifies reviews across a 10-theme taxonomy (No-Show disputes, GPS telemetry, booking boundary bugs, etc.).
- Maps themes directly to engineering and operations squad owners.
- Calculates Trailing-30d rating, 7d vs prior-7d velocity, and 1-star share WoW.

### 2. No-Show Fairness Shield (`services/no_show_fairness_engine.py`)
Attacks the #1 driver of 1-star reviews (unfair salary deductions):
- **Driver Verification Guardrail:** Disallows drivers from marking No-Show unless verified within 50m of pickup pin with $\ge 180\text{s}$ stationary dwell.
- **Evidence Card:** Displays who marked absent, driver GPS distance, and dwell timer.
- **1-Tap Auto-Reversal:** Evaluates telemetry audit logs and automatically revokes payroll deductions without manual HR intervention.

### 3. Distributed Idempotent Booking API (`services/idempotent_booking_api.py`)
- **Idempotency-Key Header:** Prevents duplicate bookings and double billing during cellular retry bursts.
- **Transactional Outbox:** Atomically commits trip booking and push notification records in a single ACID transaction.
- **Midnight Boundary Gate:** Unit-tested timezone conversions protecting night-shift rosters (23:30–00:30).

---

## 📋 Start-Tomorrow Jira Engineering Backlog

| Ticket | Title | Assigned Owner | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **RP-1** | Export Play Console 90-Day Telemetry | FDE / Product | Secure Play Console API; export review dumps, vitals, crash & ANR rates. |
| **RP-2** | Automate Ratings Pulse Weekly Cron | FDE / DevOps | Schedule `ratings_pulse.py` every Monday at 08:30 IST via GitHub Actions. |
| **RP-3** | Establish 48h Review Response SLA | Customer Success | 100% of 1–3★ reviews receive personalized human triage within 48h. |
| **RP-4** | Suppress Rating Prompts on Late Trips | Mobile Eng | Suppress in-app rating prompts on trips delayed $>10\text{m}$ or flagged `DISPUTED`. |
| **RP-5** | Stale-GPS Indicator & Confidence Band | Android / iOS Eng | Desaturate vehicle pin if location $>30\text{s}$ old; display ETA confidence range. |
| **RP-6** | Driver Geofence Dwell & Proximity Lock | Driver App Eng | Disable "Mark No-Show" button unless driver is within 50m and dwell $\ge 180\text{s}$. |
| **RP-7** | Pre-Pickup Geofence Proximity Push | Platform Backend | Send high-priority FCM notification at 200m: *"Cab is arriving. Tap to check in."* |
| **RP-8** | One-Tap Dispute & Auto-Reversal | Mobile + Backend | Display Evidence Card; auto-reverse no-show if driver dwell $<180\text{s}$. |
| **RP-9** | Idempotent Booking & Outbox | Core Backend Eng | Attach `Idempotency-Key` header; commit booking + notification outbox atomically. |
| **RP-10** | Client-Side Fleet Map Filter | Mobile Eng | Filter map to render exclusively the assigned vehicle polyline and plate. |
| **RP-11** | Midnight Boundary Shift Date Fix | Mobile + Backend | Fix timezone date conversions for 23:30–00:30 night rosters in CI unit tests. |
| **RP-12** | Google In-App Review API Integration | Android Eng | Invoke `requestReviewFlow` strictly after OTP-verified on-time drops. |

---

## 🚀 Quick Start & Local Execution

### 1. Run the No-Show Fairness Test Harness:
```bash
python3 services/no_show_fairness_engine.py
```

### 2. Run the Idempotent Booking API Test Harness:
```bash
python3 services/idempotent_booking_api.py
```

### 3. Run the Ratings Pulse Telemetry Engine:
```bash
pip install google-play-scraper pandas tabulate
python3 ratings_pulse/ratings_pulse.py --app com.moveinsync.ets --count 1000 --out pulse_out
```

### 4. View the Interactive Dashboard:
Open `dashboard/index.html` in any web browser to test the interactive No-Show dispute simulator and stale GPS toggle.

---

## 📄 Case Study Document
The complete 12-page executive case study document is available at:  
👉 **[`docs/MoveInSync_FDE_PlayStore_Turnaround_Case_Study.pdf`](docs/MoveInSync_FDE_PlayStore_Turnaround_Case_Study.pdf)**
