"""
CWMOS Phase 2 — Realistic Synthetic Dataset Generator
======================================================
Hospital floor: 80 m x 60 m, 1 m2 grid cells
8 Access Points, ITU-R indoor path-loss model, 3 obstacle types,
5 GHz channel plan with 2 deliberate co-channel conflicts,
200 device traces over 24 h, 3 injected failure states.

Run:
    python generate_dataset.py

Outputs (written to ./data/):
    floor_map.json / floor_map.csv
    ap_config.json / ap_config.csv
    crowdsource_samples.json / crowdsource_samples.csv
    channel_utilisation.json / channel_utilisation.csv
    failure_events.json
    data_dictionary.json
"""

import json
import csv
import math
import random
import os
from datetime import datetime, timedelta, timezone

random.seed(42)          # reproducible
OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------------------------
# 1. CONSTANTS & SYSTEM CONFIG (matches SystemConfig defaults from Deliverable 1)
# -------------------------------------------------------------------------------
FLOOR_W = 80   # metres, x-axis
FLOOR_H = 60   # metres, y-axis
FREQ_GHZ = 5.0
FREQ_MHZ = 5000.0
TX_POWER_DBM = 20.0
RSSI_DEAD_ZONE_THRESHOLD = -75.0   # dBm
GAUSSIAN_SIGMA = 2.0               # dB noise sigma
LF = 0                             # single-floor, no floor penetration loss

# -------------------------------------------------------------------------------
# 2. FLOOR-PLAN ZONE MAP
#    Zones: (x_min, x_max, y_min, y_max) half-open [min, max)
# -------------------------------------------------------------------------------
ZONES = {
    # Six patient wards
    "ward_A":        {"x": (0,  20), "y": (30, 60), "zone_type": "ward",      "N": 28},
    "ward_B":        {"x": (20, 40), "y": (30, 60), "zone_type": "ward",      "N": 28},
    "ward_C":        {"x": (40, 60), "y": (30, 60), "zone_type": "ward",      "N": 28},
    "ward_D":        {"x": (0,  20), "y": (0,  25), "zone_type": "ward",      "N": 28},
    "ward_E":        {"x": (20, 40), "y": (0,  25), "zone_type": "ward",      "N": 28},
    "ward_F":        {"x": (40, 60), "y": (0,  25), "zone_type": "ward",      "N": 28},
    # Two operating theatres
    "theatre_1":     {"x": (60, 72), "y": (40, 60), "zone_type": "theatre",   "N": 28},
    "theatre_2":     {"x": (60, 72), "y": (20, 40), "zone_type": "theatre",   "N": 28},
    # ICU
    "icu":           {"x": (60, 80), "y": (0,  20), "zone_type": "icu",       "N": 28},
    # Corridors (main horizontal + vertical spines)
    "corridor_h":    {"x": (0,  72), "y": (25, 30), "zone_type": "corridor",  "N": 30},
    "corridor_v":    {"x": (72, 80), "y": (20, 60), "zone_type": "corridor",  "N": 30},
    # Lift bank
    "lift_bank":     {"x": (72, 80), "y": (55, 60), "zone_type": "lift",      "N": 30},
    # Guest waiting
    "guest_waiting": {"x": (72, 80), "y": (0,  20), "zone_type": "waiting",   "N": 28},
    # Radiology (lead-lined)
    "radiology":     {"x": (60, 72), "y": (0,  20), "zone_type": "radiology", "N": 28},
    # Steel equipment store
    "equip_store":   {"x": (60, 72), "y": (17, 22), "zone_type": "store",     "N": 30},
    # Kitchen + laundry block
    "kitchen":       {"x": (0,  15), "y": (0,   8), "zone_type": "kitchen",   "N": 30},
}

# Signal obstacles: (x_min, x_max, y_min, y_max, extra_wall_loss_db)
OBSTACLES = [
    {"id": "radiology_wall",   "x": (60, 72), "y": (0,  20), "loss_db": 25.0,
     "description": "Lead-lined radiology room"},
    {"id": "equip_store_wall", "x": (60, 72), "y": (17, 22), "loss_db": 18.0,
     "description": "Steel equipment store"},
    {"id": "kitchen_wall",     "x": (0,  15), "y": (0,   8), "loss_db": 12.0,
     "description": "Laundry and kitchen block"},
]

# -------------------------------------------------------------------------------
# 3. ACCESS POINT DEFINITIONS
# Channel plan: 36,40,44,48,149,153,157,161 (5 GHz non-overlapping)
# Co-channel conflicts:
#   AP-1 and AP-3 both on CH 36  (ward_A and ward_C -- adjacent coverage)
#   AP-7 and AP-8 both on CH 153 (theatre_1 and theatre_2 -- adjacent)
# -------------------------------------------------------------------------------
ACCESS_POINTS = [
    {"id": "AP-1", "x": 10.0, "y": 45.0, "channel": 36,  "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:01", "zone": "ward_A"},
    {"id": "AP-2", "x": 30.0, "y": 45.0, "channel": 40,  "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:02", "zone": "ward_B"},
    {"id": "AP-3", "x": 50.0, "y": 45.0, "channel": 36,  "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:03", "zone": "ward_C"},
    {"id": "AP-4", "x": 10.0, "y": 12.0, "channel": 44,  "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:04", "zone": "ward_D"},
    {"id": "AP-5", "x": 30.0, "y": 12.0, "channel": 48,  "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:05", "zone": "ward_E"},
    {"id": "AP-6", "x": 50.0, "y": 12.0, "channel": 149, "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:06", "zone": "ward_F"},
    {"id": "AP-7", "x": 66.0, "y": 50.0, "channel": 153, "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:07", "zone": "theatre_1"},
    {"id": "AP-8", "x": 66.0, "y": 30.0, "channel": 153, "tx_power_dbm": 20.0, "band": "5GHz", "bssid": "AA:BB:CC:DD:EE:08", "zone": "theatre_2"},
]

CO_CHANNEL_CONFLICTS = [
    {"ap_a": "AP-1", "ap_b": "AP-3", "channel": 36,  "reason": "Adjacent ward coverage overlap"},
    {"ap_a": "AP-7", "ap_b": "AP-8", "channel": 153, "reason": "Adjacent theatres -- same channel assignment"},
]

# -------------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -------------------------------------------------------------------------------

def get_zone(x, y):
    for zone_id, props in ZONES.items():
        xr, yr = props["x"], props["y"]
        if xr[0] <= x < xr[1] and yr[0] <= y < yr[1]:
            return zone_id, props
    return "corridor_h", ZONES["corridor_h"]

def get_N(x, y):
    _, props = get_zone(x, y)
    return props["N"]

def obstacle_wall_loss(ax, ay, cx, cy):
    """
    Total additional wall loss (dB) for AP at (ax,ay) serving cell at (cx,cy).
    Adds loss if cell is inside an obstacle zone, or if the signal path crosses one.
    """
    total_loss = 0.0
    for obs in OBSTACLES:
        ox0, ox1 = obs["x"]
        oy0, oy1 = obs["y"]
        loss = obs["loss_db"]
        cell_inside = (ox0 <= cx < ox1 and oy0 <= cy < oy1)
        ap_inside   = (ox0 <= ax < ox1 and oy0 <= ay < oy1)
        if cell_inside:
            total_loss += loss
        elif not ap_inside:
            dx = cx - ax
            dy = cy - ay
            intersects = False
            for step in range(1, 10):
                t = step / 10.0
                sx = ax + t * dx
                sy = ay + t * dy
                if ox0 <= sx < ox1 and oy0 <= sy < oy1:
                    intersects = True
                    break
            if intersects:
                total_loss += loss
    return total_loss

def itu_r_path_loss(d_m, N, f_mhz=FREQ_MHZ, Lf=LF):
    """
    ITU-R P.1238: L = 20*log10(f_MHz) + N*log10(d_m) + Lf - 28  [dB]
    d clamped to >= 0.5 m.
    """
    d = max(d_m, 0.5)
    return 20 * math.log10(f_mhz) + N * math.log10(d) + Lf - 28

def compute_rssi(ap, cx, cy, offline=False):
    if offline:
        noise = random.gauss(0, GAUSSIAN_SIGMA)
        return round(-90.0 + noise, 2), 0.0, 0.0, round(noise, 2)
    dx = cx - ap["x"]
    dy = cy - ap["y"]
    d = math.sqrt(dx*dx + dy*dy)
    N = get_N(cx, cy)
    path_loss = itu_r_path_loss(d, N)
    wall_loss = obstacle_wall_loss(ap["x"], ap["y"], cx, cy)
    noise = random.gauss(0, GAUSSIAN_SIGMA)
    rssi = ap["tx_power_dbm"] - path_loss - wall_loss + noise
    return round(rssi, 2), round(path_loss, 2), round(wall_loss, 2), round(noise, 2)

def noise_floor_dbm():
    return round(random.gauss(-95, 1.5), 2)

def snr_from_rssi(rssi, nf):
    return round(rssi - nf, 2)

# -------------------------------------------------------------------------------
# 5. FLOOR MAP -- one record per 1 m2 grid cell
# -------------------------------------------------------------------------------
print("[1/6] Computing floor map heatmap (80x60 = 4800 cells)...")

floor_cells = []

for cy in range(FLOOR_H):
    for cx in range(FLOOR_W):
        zone_id, zone_props = get_zone(cx, cy)
        best_rssi  = -999.0
        best_ap    = None
        per_ap_rssi = {}

        for ap in ACCESS_POINTS:
            rssi, pl, wl, ns = compute_rssi(ap, cx, cy)
            per_ap_rssi[ap["id"]] = rssi
            if rssi > best_rssi:
                best_rssi = rssi
                best_ap   = ap["id"]

        is_dead_zone = (best_rssi <= RSSI_DEAD_ZONE_THRESHOLD)
        nf  = noise_floor_dbm()
        snr = snr_from_rssi(best_rssi, nf)

        cell = {
            "cell_x_m":        cx,
            "cell_y_m":        cy,
            "zone_id":         zone_id,
            "zone_type":       zone_props["zone_type"],
            "best_ap_id":      best_ap,
            "best_rssi_dbm":   round(best_rssi, 2),
            "noise_floor_dbm": nf,
            "snr_db":          snr,
            "is_dead_zone":    is_dead_zone,
        }
        for ap in ACCESS_POINTS:
            cell[f"rssi_{ap['id']}_dbm"] = per_ap_rssi[ap["id"]]

        floor_cells.append(cell)

total_cells     = len(floor_cells)
dead_zone_count = sum(1 for c in floor_cells if c["is_dead_zone"])
print(f"    Total cells: {total_cells}  |  Dead zones: {dead_zone_count}  ({100*dead_zone_count/total_cells:.1f}%)")

# -------------------------------------------------------------------------------
# 6. CHANNEL UTILISATION -- per AP, per hour, over 24 hours
# -------------------------------------------------------------------------------
print("[2/6] Generating channel utilisation time-series...")

BASE_DATE = datetime(2026, 9, 1, 0, 0, 0, tzinfo=timezone.utc)

def utilisation_sample(hour, ap_id):
    if ap_id == "AP-5" and 14 <= hour < 16:
        return 0.0   # AP-5 offline
    if 7 <= hour <= 9:
        return round(random.uniform(60, 85), 1)
    elif 22 <= hour or hour < 6:
        return round(random.uniform(10, 25), 1)
    else:
        return round(random.uniform(30, 55), 1)

channel_utilisation = []
for ap in ACCESS_POINTS:
    for hour in range(24):
        ts   = BASE_DATE + timedelta(hours=hour)
        util = utilisation_sample(hour, ap["id"])
        channel_utilisation.append({
            "ap_id":           ap["id"],
            "channel":         ap["channel"],
            "hour_utc":        hour,
            "timestamp_utc":   ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "utilisation_pct": util,
            "time_window": ("peak_clinical"    if 7 <= hour <= 9
                             else "low_load"   if (22 <= hour or hour < 6)
                             else "standard_clinical"),
        })

# -------------------------------------------------------------------------------
# 7. CROWDSOURCE DEVICE TRACES -- 200 devices over 24 hours
# -------------------------------------------------------------------------------
print("[3/6] Simulating 200 device traces (crowdsource samples)...")

DEVICE_TYPE_WEIGHTS = {
    "clinical_device": 0.25,
    "staff_laptop":    0.35,
    "guest_phone":     0.30,
    "iot_sensor":      0.10,
}

DEVICE_ZONE_PREFS = {
    "clinical_device": ["ward_A","ward_B","ward_C","ward_D","ward_E","ward_F","icu","theatre_1","theatre_2"],
    "staff_laptop":    ["ward_A","ward_B","ward_C","ward_D","ward_E","ward_F","corridor_h","corridor_v"],
    "guest_phone":     ["guest_waiting","corridor_h","lift_bank"],
    "iot_sensor":      ["ward_A","ward_B","ward_C","ward_D","ward_E","ward_F","icu"],
}

def weighted_choice(d):
    keys = list(d.keys())
    weights = list(d.values())
    return random.choices(keys, weights=weights, k=1)[0]

def random_position_in_zone(zone_id):
    props = ZONES[zone_id]
    x = random.uniform(props["x"][0], props["x"][1] - 0.01)
    y = random.uniform(props["y"][0], props["y"][1] - 0.01)
    return x, y

def random_position_anywhere():
    return random.uniform(0, FLOOR_W - 0.01), random.uniform(0, FLOOR_H - 0.01)

def find_best_ap_for_device(x, y, offline_ap, microwave_active):
    """Return (best_ap, rssi, noise_floor, snr) with failure injections applied."""
    best_rssi = -999.0
    best_ap   = None
    cx, cy    = int(x), int(y)

    for ap in ACCESS_POINTS:
        if offline_ap and ap["id"] == offline_ap:
            continue
        rssi, _, _, _ = compute_rssi(ap, cx, cy)
        if rssi > best_rssi:
            best_rssi = rssi
            best_ap   = ap

    if best_ap is None:
        return None, -90.0, noise_floor_dbm(), -5.0

    nf  = noise_floor_dbm()
    snr = snr_from_rssi(best_rssi, nf)

    # Microwave burst: CH36, kitchen zone only
    kz = ZONES["kitchen"]
    in_kitchen = (kz["x"][0] <= x < kz["x"][1] and kz["y"][0] <= y < kz["y"][1])
    if microwave_active and best_ap["channel"] == 36 and in_kitchen:
        snr = round(snr - 15.0, 2)
        nf  = round(nf  + 15.0, 2)

    return best_ap, round(best_rssi, 2), nf, snr

crowdsource_samples = []
SAMPLE_ID = 1

for device_idx in range(200):
    device_type = weighted_choice(DEVICE_TYPE_WEIGHTS)
    device_id   = f"{device_type[:3].upper()}-{device_idx+1:04d}"
    pref_zones  = DEVICE_ZONE_PREFS[device_type]

    # IoT sensors produce more readings (nearly stationary); mobiles roam
    num_readings = random.randint(20, 48) if device_type == "iot_sensor" else random.randint(3, 8)

    for _ in range(num_readings):
        hour_frac = random.uniform(0, 24)
        hour_int  = int(hour_frac)
        ts = BASE_DATE + timedelta(hours=hour_frac)

        if device_type == "iot_sensor":
            zone_id = random.choice(pref_zones)
            x, y    = random_position_in_zone(zone_id)
        else:
            if random.random() < 0.70:
                zone_id = random.choice(pref_zones)
                x, y    = random_position_in_zone(zone_id)
            else:
                x, y    = random_position_anywhere()
                zone_id, _ = get_zone(int(x), int(y))

        # Inject failure conditions
        offline_ap       = "AP-5" if 14 <= hour_int < 16 else None
        microwave_active = (12.5 <= hour_frac <= 13.0)

        lz = ZONES["lift_bank"]
        is_lift_bank = (lz["x"][0] <= x < lz["x"][1] and lz["y"][0] <= y < lz["y"][1])

        best_ap, rssi, nf, snr = find_best_ap_for_device(x, y, offline_ap, microwave_active)

        sample = {
            "sample_id":              SAMPLE_ID,
            "device_id":              device_id,
            "device_type":            device_type,
            "timestamp_utc":          ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hour_utc":               hour_int,
            "x_m":                    round(x, 2),
            "y_m":                    round(y, 2),
            "zone_id":                zone_id,
            "connected_ap_id":        best_ap["id"] if best_ap else "NONE",
            "channel":                best_ap["channel"] if best_ap else 0,
            "rssi_dbm":               rssi,
            "noise_floor_dbm":        nf,
            "snr_db":                 snr,
            "ap5_offline":            (offline_ap == "AP-5"),
            "microwave_burst_active": microwave_active,
            "is_lift_bank":           is_lift_bank,
            "trusted":                True,
        }
        crowdsource_samples.append(sample)
        SAMPLE_ID += 1

# Mark lift-bank samples with fewer than 3 readings per hour as untrusted
lift_per_hour = {}
for s in crowdsource_samples:
    if s["is_lift_bank"]:
        h = s["hour_utc"]
        lift_per_hour[h] = lift_per_hour.get(h, 0) + 1

for s in crowdsource_samples:
    if s["is_lift_bank"] and lift_per_hour.get(s["hour_utc"], 0) < 3:
        s["trusted"] = False

untrusted = sum(1 for s in crowdsource_samples if not s["trusted"])
print(f"    Crowdsource samples generated: {len(crowdsource_samples)}")
print(f"    Untrusted (lift bank sparse): {untrusted}")

# -------------------------------------------------------------------------------
# 8. FAILURE EVENTS LOG
# -------------------------------------------------------------------------------
print("[4/6] Recording failure events...")

failure_events = [
    {
        "event_id":         "FAIL-001",
        "event_type":       "AP_OFFLINE",
        "ap_id":            "AP-5",
        "channel":          48,
        "start_utc":        "2026-09-01T14:00:00Z",
        "end_utc":          "2026-09-01T16:00:00Z",
        "duration_min":     120,
        "effect":           "ward_E cells drop to approx -90 dBm; dead-zone count increases",
        "affected_zone":    "ward_E",
        "rssi_impact_dbm":  -90.0,
        "snr_impact_db":    None,
        "samples_per_hour_max": None,
    },
    {
        "event_id":         "FAIL-002",
        "event_type":       "INTERFERENCE_BURST",
        "ap_id":            "AP-1",
        "channel":          36,
        "start_utc":        "2026-09-01T12:30:00Z",
        "end_utc":          "2026-09-01T13:00:00Z",
        "duration_min":     30,
        "effect":           "Microwave oven on CH36 in kitchen block; SNR drops 15 dB, noise floor rises 15 dB",
        "affected_zone":    "kitchen",
        "rssi_impact_dbm":  None,
        "snr_impact_db":    -15.0,
        "samples_per_hour_max": None,
    },
    {
        "event_id":         "FAIL-003",
        "event_type":       "SPARSE_COVERAGE",
        "ap_id":            "AP-7",
        "channel":          153,
        "start_utc":        "2026-09-01T00:00:00Z",
        "end_utc":          "2026-09-01T23:59:59Z",
        "duration_min":     1440,
        "effect":           "Lift bank zone <3 crowdsource samples/hour; zone flagged UNTRUSTED per SystemConfig crowdsource_min_samples_for_trust=5",
        "affected_zone":    "lift_bank",
        "rssi_impact_dbm":  None,
        "snr_impact_db":    None,
        "samples_per_hour_max": 2,
    },
]

# -------------------------------------------------------------------------------
# 9. DATA DICTIONARY
# -------------------------------------------------------------------------------
print("[5/6] Writing data dictionary...")

data_dictionary = {
    "dataset_name": "CWMOS Phase 2 Synthetic Dataset",
    "version": "1.0",
    "generated_at": "2026-09-07T00:00:00Z",
    "floor_dimensions_m": {"width": FLOOR_W, "height": FLOOR_H},
    "grid_resolution_m": 1,
    "signal_model": "ITU-R P.1238: L = 20*log10(f_MHz) + N*log10(d_m) + Lf - 28",
    "frequency_mhz": FREQ_MHZ,
    "tx_power_dbm": TX_POWER_DBM,
    "gaussian_noise_sigma_db": GAUSSIAN_SIGMA,
    "rssi_dead_zone_threshold_dbm": RSSI_DEAD_ZONE_THRESHOLD,
    "co_channel_conflicts": CO_CHANNEL_CONFLICTS,
    "obstacles": OBSTACLES,
    "path_loss_exponents": {
        "corridor": 30,
        "open_ward_or_room": 28,
        "note": "Per ITU-R P.1238 for office/residential, adapted for clinical environment"
    },
    "failure_states_injected": [f["event_id"] for f in failure_events],
    "tables": {
        "floor_map": {
            "file_json":  "floor_map.json",
            "file_csv":   "floor_map.csv",
            "row_count":  total_cells,
            "description": "Per-grid-cell RF coverage snapshot (80x60 = 4800 rows)",
            "primary_key": ["cell_x_m", "cell_y_m"],
            "columns": {
                "cell_x_m":        {"type": "int",   "unit": "m",   "description": "Cell x-coordinate (0 to 79)"},
                "cell_y_m":        {"type": "int",   "unit": "m",   "description": "Cell y-coordinate (0 to 59)"},
                "zone_id":         {"type": "str",   "unit": None,  "description": "Hospital zone identifier"},
                "zone_type":       {"type": "str",   "unit": None,  "description": "ward | theatre | icu | corridor | lift | waiting | radiology | store | kitchen"},
                "best_ap_id":      {"type": "str",   "unit": None,  "description": "ID of AP with highest RSSI at this cell (best-server)"},
                "best_rssi_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI of best-server AP. Dead zone if <= -75 dBm"},
                "noise_floor_dbm": {"type": "float", "unit": "dBm", "description": "Simulated ambient thermal noise floor"},
                "snr_db":          {"type": "float", "unit": "dB",  "description": "Signal-to-noise ratio (best_rssi - noise_floor)"},
                "is_dead_zone":    {"type": "bool",  "unit": None,  "description": "True when best_rssi_dbm <= rssi_dead_zone_threshold (-75 dBm)"},
                "rssi_AP-1_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-1 at this cell"},
                "rssi_AP-2_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-2 at this cell"},
                "rssi_AP-3_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-3 at this cell"},
                "rssi_AP-4_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-4 at this cell"},
                "rssi_AP-5_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-5 at this cell"},
                "rssi_AP-6_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-6 at this cell"},
                "rssi_AP-7_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-7 at this cell"},
                "rssi_AP-8_dbm":   {"type": "float", "unit": "dBm", "description": "RSSI from AP-8 at this cell"},
            }
        },
        "ap_config": {
            "file_json":  "ap_config.json",
            "file_csv":   "ap_config.csv",
            "row_count":  len(ACCESS_POINTS),
            "description": "Access point configuration records (8 rows)",
            "primary_key": ["id"],
            "columns": {
                "id":           {"type": "str",   "unit": None,  "description": "AP identifier (AP-1 to AP-8)"},
                "x":            {"type": "float", "unit": "m",   "description": "AP ceiling-mount x-position"},
                "y":            {"type": "float", "unit": "m",   "description": "AP ceiling-mount y-position"},
                "channel":      {"type": "int",   "unit": None,  "description": "Assigned 5 GHz channel"},
                "tx_power_dbm": {"type": "float", "unit": "dBm", "description": "Transmit power"},
                "band":         {"type": "str",   "unit": None,  "description": "Frequency band (5GHz)"},
                "bssid":        {"type": "str",   "unit": None,  "description": "AP MAC-format BSSID"},
                "zone":         {"type": "str",   "unit": None,  "description": "Zone where AP is ceiling-mounted"},
            }
        },
        "crowdsource_samples": {
            "file_json":  "crowdsource_samples.json",
            "file_csv":   "crowdsource_samples.csv",
            "row_count":  len(crowdsource_samples),
            "description": "Simulated device probe records (200 devices, variable readings per device)",
            "primary_key": ["sample_id"],
            "columns": {
                "sample_id":              {"type": "int",   "unit": None,  "description": "Unique probe record ID"},
                "device_id":              {"type": "str",   "unit": None,  "description": "Pseudonymised device identifier"},
                "device_type":            {"type": "str",   "unit": None,  "description": "clinical_device | staff_laptop | guest_phone | iot_sensor"},
                "timestamp_utc":          {"type": "str",   "unit": None,  "description": "ISO-8601 UTC measurement timestamp"},
                "hour_utc":               {"type": "int",   "unit": "h",   "description": "Hour of day (0 to 23)"},
                "x_m":                    {"type": "float", "unit": "m",   "description": "Device x-position on floor plan"},
                "y_m":                    {"type": "float", "unit": "m",   "description": "Device y-position on floor plan"},
                "zone_id":                {"type": "str",   "unit": None,  "description": "Zone containing device at time of reading"},
                "connected_ap_id":        {"type": "str",   "unit": None,  "description": "AP the device was associated with"},
                "channel":                {"type": "int",   "unit": None,  "description": "Channel of connected AP"},
                "rssi_dbm":               {"type": "float", "unit": "dBm", "description": "Measured RSSI at device"},
                "noise_floor_dbm":        {"type": "float", "unit": "dBm", "description": "Measured noise floor (elevated during microwave burst)"},
                "snr_db":                 {"type": "float", "unit": "dB",  "description": "SNR; reduced 15 dB during microwave burst in kitchen zone"},
                "ap5_offline":            {"type": "bool",  "unit": None,  "description": "True during AP-5 outage (14:00 to 16:00)"},
                "microwave_burst_active": {"type": "bool",  "unit": None,  "description": "True during CH36 microwave interference (12:30 to 13:00)"},
                "is_lift_bank":           {"type": "bool",  "unit": None,  "description": "True if device is in lift bank zone"},
                "trusted":                {"type": "bool",  "unit": None,  "description": "False when zone has <3 samples/hour -- unreliable zone per SystemConfig"},
            }
        },
        "channel_utilisation": {
            "file_json":  "channel_utilisation.json",
            "file_csv":   "channel_utilisation.csv",
            "row_count":  len(channel_utilisation),
            "description": "Hourly channel utilisation per AP (8 APs x 24 hours = 192 rows)",
            "primary_key": ["ap_id", "hour_utc"],
            "columns": {
                "ap_id":           {"type": "str",   "unit": None, "description": "AP identifier"},
                "channel":         {"type": "int",   "unit": None, "description": "Assigned 5 GHz channel"},
                "hour_utc":        {"type": "int",   "unit": "h",  "description": "Hour of day (0 to 23)"},
                "timestamp_utc":   {"type": "str",   "unit": None, "description": "ISO-8601 UTC (start of hour)"},
                "utilisation_pct": {"type": "float", "unit": "%",  "description": "Channel busy fraction: 60-85% peak, 30-55% standard, 10-25% overnight, 0% during AP-5 outage"},
                "time_window":     {"type": "str",   "unit": None, "description": "SystemConfig time-window label"},
            }
        },
        "failure_events": {
            "file_json":  "failure_events.json",
            "row_count":  len(failure_events),
            "description": "Injected failure states and their parameters (3 rows)",
            "primary_key": ["event_id"],
            "columns": {
                "event_id":              {"type": "str",   "unit": None,  "description": "Failure event identifier"},
                "event_type":            {"type": "str",   "unit": None,  "description": "AP_OFFLINE | INTERFERENCE_BURST | SPARSE_COVERAGE"},
                "ap_id":                 {"type": "str",   "unit": None,  "description": "Primary AP affected"},
                "channel":               {"type": "int",   "unit": None,  "description": "Channel involved"},
                "start_utc":             {"type": "str",   "unit": None,  "description": "Failure start (ISO-8601)"},
                "end_utc":               {"type": "str",   "unit": None,  "description": "Failure end (ISO-8601)"},
                "duration_min":          {"type": "int",   "unit": "min", "description": "Duration in minutes"},
                "effect":                {"type": "str",   "unit": None,  "description": "Signal impact description"},
                "affected_zone":         {"type": "str",   "unit": None,  "description": "Primary hospital zone affected"},
                "rssi_impact_dbm":       {"type": "float", "unit": "dBm", "description": "RSSI drop caused by failure (null if not applicable)"},
                "snr_impact_db":         {"type": "float", "unit": "dB",  "description": "SNR reduction caused by failure (null if not applicable)"},
                "samples_per_hour_max":  {"type": "int",   "unit": None,  "description": "Max samples per hour in affected zone (null if not applicable)"},
            }
        }
    }
}

# -------------------------------------------------------------------------------
# 10. WRITE ALL OUTPUTS
# -------------------------------------------------------------------------------
print("[6/6] Writing JSON and CSV outputs...")

def write_json(data, filename):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    size_kb = os.path.getsize(path) // 1024
    print(f"    OK  {path}  ({size_kb} KB)")

def write_csv(records, filename):
    if not records:
        return
    path = os.path.join(OUT_DIR, filename)
    keys = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    size_kb = os.path.getsize(path) // 1024
    print(f"    OK  {path}  ({size_kb} KB)")

write_json(floor_cells,            "floor_map.json")
write_csv(floor_cells,             "floor_map.csv")
write_json(ACCESS_POINTS,          "ap_config.json")
write_csv(ACCESS_POINTS,           "ap_config.csv")
write_json(crowdsource_samples,    "crowdsource_samples.json")
write_csv(crowdsource_samples,     "crowdsource_samples.csv")
write_json(channel_utilisation,    "channel_utilisation.json")
write_csv(channel_utilisation,     "channel_utilisation.csv")
write_json(failure_events,         "failure_events.json")
write_json(data_dictionary,        "data_dictionary.json")

print("\n" + "="*60)
print("DATASET GENERATION COMPLETE")
print("="*60)
print(f"  Floor grid             : {FLOOR_W}x{FLOOR_H} = {total_cells} cells")
print(f"  Dead zones             : {dead_zone_count} cells ({100*dead_zone_count/total_cells:.1f}%)")
print(f"  Access Points          : {len(ACCESS_POINTS)}")
print(f"  Co-channel conflicts   : {len(CO_CHANNEL_CONFLICTS)}")
print(f"  Crowdsource samples    : {len(crowdsource_samples)}")
print(f"  Untrusted samples      : {untrusted}")
print(f"  Channel util rows      : {len(channel_utilisation)}")
print(f"  Failure events         : {len(failure_events)}")
print(f"\nAll files written to ./{OUT_DIR}/")
