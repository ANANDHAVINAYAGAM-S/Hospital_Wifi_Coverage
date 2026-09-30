# Clinical Wi-Fi Monitoring & Optimization System (CWMOS)

## System Overview
**CWMOS** is a physics-informed, dynamic wireless quality-of-service (QoS) telemetry and Radio Resource Management (RRM) optimization platform engineered for critical healthcare environments. It combines **ITU-R P.1238 indoor radio propagation modeling** with a **2D Kalman filter crowdsource fusion engine** to track wireless coverage, detect dead zones ($<-75.0\text{ dBm}$ RSSI), eliminate co-channel interference (CCI), and perform automated self-healing during access point (AP) outages.

---

## Workspace Structure

```
project sem 5/
├── cwmos_prototype.html                 # Interactive Single-File React + Tailwind Web App (5 Screens)
├── generate_dataset.py                  # Realistic Synthetic Dataset Generator
├── compare_algorithms.py                 # Algorithm Comparison Engine (IDW vs Kalman Fusion)
├── verify_dataset.py                    # Dataset Integrity Verifier
├── auto_tuning_engine.py                # Phase 5 RRM Closed-Loop Auto-Tuning Engine
├── telemetry_ingestion_pipeline.py      # Phase 6 Real-Time Telemetry Ingestion Pipeline
├── multifloor_3d_propagation.py         # Phase 7 3D Multi-Floor Radio Propagation Model
├── audit_exporter.py                    # Phase 8 30-Day Historical Analytics & SLA Exporter
├── recommendation_engine.py             # Phase 2 Optimization Recommendation Engine
├── run_experiment.py                    # Phase 2 Measurable Experiment Runner (10-Step Benchmark)
├── limitations_and_failure_cases.md     # Technical Report on RF Edge Cases & Safeguards
├── demo_script.md                       # Demonstration Walkthrough Guide
├── deliverable_traceability_matrix.md   # Requirement-to-Code Traceability Table
├── README.md                            # Main Repository & Execution Guide
├── data/                                # Generated Datasets (JSON & CSV)
│   ├── floor_map.json / .csv
│   ├── ap_config.json / .csv
│   ├── crowdsource_samples.json / .csv
│   ├── channel_utilisation.json / .csv
│   ├── failure_events.json
│   ├── data_dictionary.json
│   └── auto_tuned_ap_config.json / .csv
└── results/                             # Benchmark Outputs & Audit Artifacts
    ├── approach_a_heatmap.json / .csv   # IDW Heatmap
    ├── approach_b_heatmap.json / .csv   # Kalman Fusion Heatmap
    ├── comparison_metrics.json
    ├── comparison_report.txt
    ├── rrm_optimization_report.txt
    ├── rrm_metrics.json
    ├── telemetry_ingestion_log.json
    ├── multifloor_3d_coverage.json
    ├── multifloor_summary_report.txt
    ├── historical_30day_sla_telemetry.csv / .json
    ├── hospital_accreditation_sla_audit.json
    ├── hospital_accreditation_sla_audit.txt
    ├── recommendations.json
    ├── experiment_results.json
    └── experiment_summary.txt
```

---

## Quick Start & Execution Guide

### 1. Launch Interactive Prototype
Double click or open [cwmos_prototype.html](file:///c:/Users/star/Downloads/project%20sem%205/cwmos_prototype.html) in any modern web browser (Chrome, Edge, Firefox, Safari).

Features 5 interactive screens:
- **Screen 1**: Role Selection (Network Engineer vs. Clinical IT Manager)
- **Screen 2**: Executive SLA & Clinical Operations Dashboard
- **Screen 3**: Interactive 2D Floor Map & Dynamic Telemetry Slider
- **Screen 4**: System Rule & Threshold Configuration Panel
- **Screen 5**: Results & Algorithm Validation Dashboard (Bar Charts, RRM Table, Sensitivity Analysis)

### 2. Run Data Pipeline & Algorithm Benchmarks

```powershell
# Step 1: Verify synthetic dataset integrity
python verify_dataset.py

# Step 2: Run IDW vs Kalman algorithm comparison
python compare_algorithms.py

# Step 3: Run Radio Resource Management (RRM) Auto-Tuning Engine
python auto_tuning_engine.py

# Step 4: Run Real-Time Telemetry Ingestion Pipeline
python telemetry_ingestion_pipeline.py --once

# Step 5: Run 3D Multi-Floor Radio Propagation Simulation
python multifloor_3d_propagation.py

# Step 6: Generate 30-Day Hospital Accreditation SLA Audit Report
python audit_exporter.py

# Step 7: Run Optimization Recommendations & Measurable Experiment Benchmark
python run_experiment.py
```

---

## Performance Summary

| Metric | Approach A (IDW) | Approach B (Kalman Fusion) | Delta |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 99.25% | **99.77%** | $+0.52\%$ |
| **Precision** | 93.11% | **100.00%** | $+6.89\%$ |
| **Recall** | 94.98% | **96.32%** | $+1.34\%$ |
| **F1 Score** | 94.04% | **98.13%** | $+4.09\%$ |
| **False Positive Rate** | 0.47% | **0.00%** | $-0.47\%$ |
| **Sparse Data F1 (5% sampling)** | 0.814 | **0.981** | $+0.168$ |

---

## Key Deliverable Documentation
- **Walkthrough Guide**: [demo_script.md](file:///c:/Users/star/Downloads/project%20sem%205/demo_script.md)
- **Edge Cases & Limitations**: [limitations_and_failure_cases.md](file:///c:/Users/star/Downloads/project%20sem%205/limitations_and_failure_cases.md)
- **Traceability Matrix**: [deliverable_traceability_matrix.md](file:///c:/Users/star/Downloads/project%20sem%205/deliverable_traceability_matrix.md)
