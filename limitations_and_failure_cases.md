# CWMOS Limitations and Failure Cases Analysis

## 1. System Overview & Scope Boundary
This document provides a formal technical assessment of the edge cases, physical propagation limitations, sensor noise boundaries, and failure modes of the **Clinical Wi-Fi Monitoring & Optimization System (CWMOS)**. While CWMOS achieves $99.77\%$ accuracy and $0.9813$ F1 score under standard operating conditions, clinical environments present non-stationary RF propagation challenges that require explicit algorithmic safeguards.

---

## 2. RF & Physical Environment Edge Cases

### 2.1 Heavy Attenuation Obstacles (Lead-Lined Radiology Shields)
- **Physical Phenomenon**: Lead-lined drywall in Radiology ($25.0\text{ dB}$ attenuation) and steel equipment stores ($18.0\text{ dB}$ attenuation) create sharp RSSI drop-offs across $1\text{ meter}$ spatial boundaries.
- **System Failure Mode**: Spatial interpolation models (such as Inverse Distance Weighting) smooth RSSI values isotropically, falsely predicting adequate coverage in dead zones behind lead shields.
- **CWMOS Mitigation**: The ITU-R P.1238 prior explicitly embeds wall attenuation loss boundaries into the 2D ray-casting engine prior to Kalman measurement updates.

### 2.2 Transient Mobile Obstacles (C-Arm X-Ray Units & Surgical Carts)
- **Physical Phenomenon**: Mobile C-arm fluoroscopy units, stainless steel surgical carts, and patient isolation curtains introduce dynamic multi-path fading ($6\text{ dB}$ to $12\text{ dB}$ temporary loss).
- **System Failure Mode**: Fixed static propagation models cannot predict transient obstacle movement without live sensor feeds.
- **CWMOS Mitigation**: The 2D Kalman filter maintains cell posterior variance $\sigma^2_{(x,y)}$. When mobile obstacles degrade local RSSI, crowdsource telemetry updates the posterior state within $1$ measurement cycle.

### 2.3 Faraday Shielding in Lift-Bank & Elevator Shafts
- **Physical Phenomenon**: Reinforced concrete lift cores and metal elevator cabs form near-total Faraday cages, reducing RSSI to $<-95\text{ dBm}$.
- **System Failure Mode**: Scarcity of probe data inside moving cabs results in high estimation variance.
- **CWMOS Mitigation**: Un-trusted Lift-Bank telemetry ($<5$ samples/hour) is automatically flagged `is_trusted=False` and excluded from Kalman state updates to prevent corrupting adjacent corridor estimates.

---

## 3. Telemetry & Sensor Noise Limitations

### 3.1 Heterogeneous Medical & Consumer Device Antennas
- **Telemetry Variance**: Clinical workstation laptops have high-gain directional antennas ($R = 9.0\text{ dB}^2$), whereas consumer IoT temperature sensors have low-gain omnidirectional chip antennas ($R = 36.0\text{ dB}^2$).
- **Mitigation**: CWMOS applies per-device measurement noise covariance weighting $R_{dev}$ in the Kalman gain equation:
  $$K_k = P_k^-(P_k^- + R_{dev})^{-1}$$

### 3.2 Non-Wi-Fi RF Interference Bursts (Microwave Ovens & Electrocautery)
- **Interference Profile**: Kitchen microwave ovens operating on $2.4\text{ GHz} / 5\text{ GHz}$ ISM bands introduce wideband noise floor spikes ($+15\text{ dB}$ noise rise), dropping SNR by $15\text{ dB}$ without altering raw RSSI.
- **Mitigation**: CWMOS monitors SNR telemetry alongside RSSI. If SNR drops below $15\text{ dB}$ while RSSI remains constant, an `INTERFERENCE_BURST` flag is raised rather than an AP failure alert.

---

## 4. Hardware Outage & Self-Healing Boundaries

### 4.1 Single AP Hardware Outage ($\text{AP-5}$ Failure in Ward E)
- **Failure State**: When $\text{AP-5}$ goes offline, Ward E cells drop to $<-90\text{ dBm}$.
- **RRM Self-Healing Action**: CWMOS dynamic Transmit Power Control (TPC) increases neighbor AP transmit power ($\text{AP-2}, \text{AP-4}, \text{AP-6}$) from $20\text{ dBm}$ to $23\text{ dBm}$.
- **Boundary Limit**: TPC cannot bridge coverage gaps if 2 adjacent APs fail simultaneously ($\text{AP-4}$ and $\text{AP-5}$ offline). Under dual-failure scenarios, physical AP deployment is required.

---

## 5. Summary of System Constraints & Safeguards

| Failure Case | Root Cause | CWMOS Algorithmic Safeguard | Residual Risk |
| :--- | :--- | :--- | :--- |
| **Radiology Shielding** | $25\text{ dB}$ Lead wall loss | ITU-R Ray-casting obstacle map | Non-standard wall modifications |
| **Sparse Lift-Bank Data** | High Faraday attenuation | Gate on sample count ($N \ge 5$) | Untested inside elevator cab |
| **Microwave Interference** | Wideband ISM noise | Dual RSSI/SNR telemetry threshold | Dynamic frequency hopping needed |
| **Dual AP Outage** | Multiple hardware failure | Emergency TPC boost to $23\text{ dBm}$ | Physical AP addition required |
