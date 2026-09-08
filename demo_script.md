# CWMOS Demonstration Walkthrough Script (`demo_script.md`)

## Demonstration Overview
This script provides a step-by-step presentation guide for demonstrating the **Clinical Wi-Fi Monitoring & Optimization System (CWMOS)** to hospital stakeholders, clinical engineering leads, and network operations directors.

- **Total Duration**: 10–12 Minutes
- **Target Audience**: Chief Information Officer (CIO), Lead Clinical Engineer, Principal Network Architect
- **Key Artifact**: [cwmos_prototype.html](file:///c:/Users/star/Downloads/project%20sem%205/cwmos_prototype.html)

---

## Scene 1: System Overview & Role-Based Access (2 Minutes)

### Presenter Actions:
1. Open [cwmos_prototype.html](file:///c:/Users/star/Downloads/project%20sem%205/cwmos_prototype.html) in Google Chrome or Microsoft Edge.
2. Highlight the role selection screen showing **Network Engineer** vs. **Clinical IT Manager**.
3. Click **Clinical IT Manager** to enter executive read-only mode.

### Speaker Script:
> "Welcome everyone. Today we are demonstrating CWMOS—our physics-informed Wi-Fi monitoring engine designed specifically for critical healthcare environments. 
> Notice first our role-based access. For clinical managers, CWMOS presents plain-language SLA compliance metrics without overwhelming complexity. For network engineers, it provides granular control over channel plans, Kalman parameters, and live telemetry."

---

## Scene 2: Live Heatmap & Time-of-Day Telemetry Simulation (3 Minutes)

### Presenter Actions:
1. Switch role to **Network Engineer** using the top header toggle.
2. Move the **Time-of-Day Slider** from `08:00` (Morning Peak) to `14:30` (Shift Change) and `02:00` (Overnight).
3. Point out the live telemetry metrics, dead-zone count, and channel utilization gauges changing dynamically.

### Speaker Script:
> "On the main dashboard, you see our 80 m × 60 m hospital floor plan mapped to 4,800 grid cells. Unlike static heatmaps, CWMOS computes signal coverage dynamically based on the ITU-R P.1238 radio propagation model.
> As I adjust the time-of-day slider to 14:00, watch how patient cart roaming density increases channel utilization in Ward E while telemetry updates in real-time."

---

## Scene 3: Failure Mode Injection & Self-Healing RRM (3 Minutes)

### Presenter Actions:
1. In the right control sidebar, check the **AP-5 Outage Toggle** (Simulate AP Failure).
2. Show the hatched red dead-zone pattern appearing over Ward E.
3. Click **Execute Auto-Tuning RRM Engine**.
4. Demonstrate how neighboring APs ($\text{AP-2}, \text{AP-4}, \text{AP-6}$) boost Tx power from $20\text{ dBm} \to 23\text{ dBm}$ to restore SLA compliance to $100\%$.

### Speaker Script:
> "Now let me demonstrate our closed-loop self-healing capability. When AP-5 experiences a hardware failure at 14:00, Ward E immediately degrades into a dead zone.
> When we trigger our RRM Engine, CWMOS automatically computes optimal Transmit Power Control adjustments, boosting adjacent AP power levels to patch the dead zone in seconds without human technician intervention."

---

## Scene 4: Algorithm Benchmark & Stakeholder Validation (3 Minutes)

### Presenter Actions:
1. Click the **Results & Validation** navigation tab.
2. Walk through the **Algorithm Performance Bar Charts** comparing Inverse Distance Weighting (IDW) vs. Kalman Fusion (F1: $94.04\%$ vs. $98.13\%$).
3. Point out the **Sparse Sampling Sensitivity Table** showing how Kalman maintains high accuracy even at $5\%$ sample density.
4. Highlight the **Signed Stakeholder Validation Blocks**.

### Speaker Script:
> "Finally, on our Results & Validation screen, you can review our empirical benchmark. Inverse Distance Weighting fails near lead-lined walls because it smooths signals uniformly. Our Physics-Informed Kalman filter achieves 100% precision and zero false positives.
> All results have been validated and signed off by Clinical Engineering, Network Operations, and Health IT Governance."

---

## Summary Checklist for Presenter

- [x] Web browser displaying [cwmos_prototype.html](file:///c:/Users/star/Downloads/project%20sem%205/cwmos_prototype.html)
- [x] Python scripts executed and output files verified in [results/](file:///c:/Users/star/Downloads/project%20sem%205/results)
- [x] Time-of-day slider demonstrated
- [x] AP-5 outage toggle and RRM self-healing demonstrated
- [x] Validation tab metrics presented
