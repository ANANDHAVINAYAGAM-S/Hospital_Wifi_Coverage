"""
CWMOS Phase 7 -- Multi-Floor & 3D Radio Propagation Model
=========================================================
3D Ray-Tracing and Inter-Floor Attenuation Propagation Engine.

Features:
1. 3D Spatial Grid: Extends 2D (80m x 60m) to 3 hospital floors (Height = 4m per floor).
2. ITU-R P.1238 Multi-Floor Loss Model:
   - Incorporates Floor Penetration Loss (LF = 15 dB for 1 floor slab, LF = 24 dB for 2 slabs).
3. Evaluates vertical RF leakage between floors (e.g. APs on Floor 2 serving Floor 1 and Floor 3).

Outputs:
   results/multifloor_3d_coverage.json
   results/multifloor_summary_report.txt
"""

import json
import math
import os
from datetime import datetime

OUT_RESULTS_DIR = "results"
os.makedirs(OUT_RESULTS_DIR, exist_ok=True)

FLOOR_W = 80
FLOOR_H = 60
FLOOR_HEIGHT_M = 4.0
NUM_FLOORS = 3
FREQ_GHZ = 5.0
RSSI_DEAD_THRESHOLD = -75.0

def calc_itu_3d_rssi(ap_x, ap_y, ap_z, tx_power, cell_x, cell_y, cell_z, extra_loss=0.0):
    dx = cell_x - ap_x
    dy = cell_y - ap_y
    dz = cell_z - ap_z
    
    dist_3d = math.sqrt(dx * dx + dy * dy + dz * dz)
    if dist_3d < 1.0:
        dist_3d = 1.0
        
    num_floors_penetrated = abs(int(round(dz / FLOOR_HEIGHT_M)))
    
    # Inter-floor penetration loss factor (ITU-R P.1238 for office/hospital)
    if num_floors_penetrated == 0:
        lf = 0.0
    elif num_floors_penetrated == 1:
        lf = 15.0  # dB for 1 floor slab
    else:
        lf = 24.0  # dB for 2 floor slabs
        
    path_loss = 20 * math.log10(FREQ_GHZ * 1000) + 30 * math.log10(dist_3d) - 28.0 + lf + extra_loss
    return tx_power - path_loss

def run_3d_simulation():
    print("Initializing 3-Floor 3D Radio Propagation Model...")
    
    with open("data/ap_config.json", encoding="utf-8") as f:
        base_aps = json.load(f)
        
    # Deploy APs across 3 floors (Floor 1: 3 APs, Floor 2: 3 APs, Floor 3: 2 APs)
    aps_3d = []
    floor_assignments = [1, 1, 1, 2, 2, 2, 3, 3]
    for ap, floor_idx in zip(base_aps, floor_assignments):
        ap_copy = dict(ap)
        ap_copy["floor"] = floor_idx
        ap_copy["z_m"] = (floor_idx - 1) * FLOOR_HEIGHT_M + 2.5 # mounted on 2.5m ceiling
        aps_3d.append(ap_copy)
        
    # Sample 3D grid (downsampled 2m step for 3 floors)
    total_cells = 0
    dead_cells_per_floor = {1: 0, 2: 0, 3: 0}
    total_cells_per_floor = {1: 0, 2: 0, 3: 0}
    
    grid_results = []
    
    for f_idx in range(1, NUM_FLOORS + 1):
        cell_z = (f_idx - 1) * FLOOR_HEIGHT_M + 1.0 # 1m desk height
        for cx in range(0, FLOOR_W, 2):
            for cy in range(0, FLOOR_H, 2):
                total_cells += 1
                total_cells_per_floor[f_idx] += 1
                
                max_rssi = -999.0
                serving_ap = None
                
                for ap in aps_3d:
                    rssi = calc_itu_3d_rssi(
                        ap["x"], ap["y"], ap["z_m"],
                        ap["tx_power_dbm"],
                        cx, cy, cell_z
                    )
                    if rssi > max_rssi:
                        max_rssi = rssi
                        serving_ap = ap["id"]
                        
                is_dead = max_rssi < RSSI_DEAD_THRESHOLD
                if is_dead:
                    dead_cells_per_floor[f_idx] += 1
                    
                grid_results.append({
                    "floor": f_idx,
                    "x_m": cx,
                    "y_m": cy,
                    "z_m": cell_z,
                    "best_rssi_dbm": round(max_rssi, 2),
                    "serving_ap_id": serving_ap,
                    "is_dead_zone": is_dead
                })

    # Summary metrics
    floor_summaries = {}
    total_dead = 0
    for f_idx in range(1, NUM_FLOORS + 1):
        d_count = dead_cells_per_floor[f_idx]
        t_count = total_cells_per_floor[f_idx]
        total_dead += d_count
        sla = ((t_count - d_count) / t_count) * 100.0
        floor_summaries[f"floor_{f_idx}"] = {
            "floor_number": f_idx,
            "total_cells": t_count,
            "dead_cells": d_count,
            "sla_compliance_pct": round(sla, 2)
        }
        
    overall_sla = ((total_cells - total_dead) / total_cells) * 100.0
    
    output_data = {
        "simulation_timestamp": datetime.utcnow().isoformat() + "Z",
        "building_dimensions": {"width_m": FLOOR_W, "length_m": FLOOR_H, "floors": NUM_FLOORS, "floor_height_m": FLOOR_HEIGHT_M},
        "ap_deployments_3d": aps_3d,
        "overall_sla_compliance_pct": round(overall_sla, 2),
        "floor_summaries": floor_summaries,
        "sample_grid_count": len(grid_results)
    }
    
    with open(os.path.join(OUT_RESULTS_DIR, "multifloor_3d_coverage.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    report = f"""======================================================================
CWMOS PHASE 7 -- 3D MULTI-FLOOR PROPAGATION & COVERAGE REPORT
======================================================================
Building Model: {NUM_FLOORS} Floors (80m x 60m per floor, 4m floor-to-floor)
Floor Slab Attenuation: LF = 15 dB (1 slab), LF = 24 dB (2 slabs)

OVERALL BUILDING COVERAGE:
  Total 3D Cells Sampled  : {total_cells}
  Overall SLA Compliance : {overall_sla:.2f}% ({total_dead} dead cells)

FLOOR BREAKDOWN:
  Floor 1: {floor_summaries['floor_1']['sla_compliance_pct']}% SLA ({floor_summaries['floor_1']['dead_cells']} dead / {floor_summaries['floor_1']['total_cells']} cells)
  Floor 2: {floor_summaries['floor_2']['sla_compliance_pct']}% SLA ({floor_summaries['floor_2']['dead_cells']} dead / {floor_summaries['floor_2']['total_cells']} cells)
  Floor 3: {floor_summaries['floor_3']['sla_compliance_pct']}% SLA ({floor_summaries['floor_3']['dead_cells']} dead / {floor_summaries['floor_3']['total_cells']} cells)

3D AP DEPLOYMENT PLAN:
"""
    for ap in aps_3d:
        report += f"  - {ap['id']} ({ap['zone']}): Floor {ap['floor']} at z={ap['z_m']}m, Ch {ap['channel']}, {ap['tx_power_dbm']} dBm\n"
        
    report += "\n======================================================================\n"
    
    with open(os.path.join(OUT_RESULTS_DIR, "multifloor_summary_report.txt"), "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"3D Multi-Floor simulation complete. Overall SLA: {overall_sla:.2f}%")
    return output_data

if __name__ == "__main__":
    run_3d_simulation()
