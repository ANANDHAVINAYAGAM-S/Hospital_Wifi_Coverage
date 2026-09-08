import json
from collections import Counter

# Floor map spot checks
with open('data/floor_map.json') as f:
    fm = json.load(f)

print('=== FLOOR MAP SPOT CHECKS ===')
c = next(x for x in fm if x['cell_x_m']==10 and x['cell_y_m']==45)
print('Cell (10,45) ward_A under AP-1: best_rssi=' + str(c['best_rssi_dbm']) + ' dBm, ap=' + c['best_ap_id'] + ', dead=' + str(c['is_dead_zone']))

c2 = next(x for x in fm if x['cell_x_m']==65 and x['cell_y_m']==10)
print('Cell (65,10) radiology (25dB wall): best_rssi=' + str(c2['best_rssi_dbm']) + ' dBm, ap=' + c2['best_ap_id'] + ', dead=' + str(c2['is_dead_zone']))

c3 = next(x for x in fm if x['cell_x_m']==79 and x['cell_y_m']==59)
print('Cell (79,59) far corner corridor: best_rssi=' + str(c3['best_rssi_dbm']) + ' dBm, ap=' + c3['best_ap_id'] + ', dead=' + str(c3['is_dead_zone']))

dead_count = sum(1 for c in fm if c['is_dead_zone'])
print('Total dead zones: ' + str(dead_count) + '/4800 (' + str(round(100*dead_count/4800,1)) + '%)')

print()
print('=== DEAD ZONES BY ZONE TYPE ===')
dz_by_zone = Counter(c['zone_type'] for c in fm if c['is_dead_zone'])
for zt, cnt in sorted(dz_by_zone.items(), key=lambda x: -x[1]):
    print('  ' + zt.ljust(15) + ': ' + str(cnt))

print()
print('=== CHANNEL UTILISATION SAMPLES ===')
with open('data/channel_utilisation.json') as f:
    cu = json.load(f)

peak    = next(x for x in cu if x['ap_id']=='AP-1' and x['hour_utc']==8)
nite    = next(x for x in cu if x['ap_id']=='AP-1' and x['hour_utc']==2)
ap5_off = next(x for x in cu if x['ap_id']=='AP-5' and x['hour_utc']==15)
print('AP-1 peak    (h=8):  ' + str(peak['utilisation_pct']) + '% -- ' + peak['time_window'])
print('AP-1 overnight(h=2): ' + str(nite['utilisation_pct']) + '% -- ' + nite['time_window'])
print('AP-5 offline  (h=15):' + str(ap5_off['utilisation_pct']) + '% -- ' + ap5_off['time_window'])

print()
print('=== CROWDSOURCE SAMPLE CHECKS ===')
with open('data/crowdsource_samples.json') as f:
    cs = json.load(f)

offline_s = [s for s in cs if s['ap5_offline']]
print('Samples during AP-5 outage: ' + str(len(offline_s)))
if offline_s:
    s = offline_s[0]
    print('  Example: zone=' + s['zone_id'] + ', ap=' + s['connected_ap_id'] + ', rssi=' + str(s['rssi_dbm']))

mw_s = [s for s in cs if s['microwave_burst_active']]
print('Samples during microwave burst: ' + str(len(mw_s)))
if mw_s:
    s = mw_s[0]
    print('  Example: zone=' + s['zone_id'] + ', snr=' + str(s['snr_db']) + ' dB')

untrusted = [s for s in cs if not s['trusted']]
print('Untrusted lift-bank samples: ' + str(len(untrusted)))

print()
print('=== DEVICE TYPE DISTRIBUTION ===')
dt = Counter(s['device_type'] for s in cs)
total = len(cs)
for k, v in sorted(dt.items(), key=lambda x: -x[1]):
    print('  ' + k.ljust(20) + ': ' + str(v) + ' (' + str(round(100*v/total,1)) + '%)')

print()
print('=== CO-CHANNEL CONFLICT CHECK ===')
ap1_ch = next(x for x in cu if x['ap_id']=='AP-1' and x['hour_utc']==8)['channel']
ap3_ch = next(x for x in cu if x['ap_id']=='AP-3' and x['hour_utc']==8)['channel']
ap7_ch = next(x for x in cu if x['ap_id']=='AP-7' and x['hour_utc']==8)['channel']
ap8_ch = next(x for x in cu if x['ap_id']=='AP-8' and x['hour_utc']==8)['channel']
print('AP-1 channel: ' + str(ap1_ch) + '  AP-3 channel: ' + str(ap3_ch) + '  (conflict: ' + str(ap1_ch==ap3_ch) + ')')
print('AP-7 channel: ' + str(ap7_ch) + '  AP-8 channel: ' + str(ap8_ch) + '  (conflict: ' + str(ap7_ch==ap8_ch) + ')')
