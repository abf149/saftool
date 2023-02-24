import os
import parse_power, parse_area, parse_latency
from parse_power import cat_names as power_cat_names, fld_names as power_fld_names

# Build csv header
# - Component name
header = ['name']
# - Power contribution breakout
for cat in power_cat_names:
    for fld in power_fld_names:
        header.append(cat+'_'+fld)
# - Total power
header.append('total_power')
# - Remaining headers
header.extend(['dyn_power_unit', \
            'leak_power_unit', \
            'absolute_total_area', \
            'combinational_area', \
            'non_combinational_area', \
            'black-box area', \
            'area_unit', \
            'critical_path_length', \
            'lvls_of_logic', \
            'critical_path_slack', \
            'critical_path_clock_latency', \
            'total_negative_slack', \
            'num_violating_paths', \
            'worst_hold_violation', \
            'total_hold_violation', \
            'num_hold_violations', \
            'latency_unit'])

fn=input('')
if fn=='header':
    print(','.join(header))
    exit()

# Name value
data = [os.path.split(fn)[-1]]

# Power values
breakdown, cat_names, dyn_power_unit, leak_power_unit = parse_power.parse_power(fn+'.power')
# Compute derived action energy
assert(dyn_power_unit=='1mW')

total_power=pwr_flds[3]
clock_period=latency_flds[3]
action_energy=(total_power)*(clock_period) # (total_power*1e12/1000)*(clock_period/1e9)
energy_unit='pJ'


area_flds, area_unit = parse_area.parse_area(fn+'.area')
latency_flds, latency_unit = parse_latency.parse_latency(fn+'.latency')
assert(latency_unit=='ns')

raise ValueError(str(breakdown))

# - float list of [absolute total area, combinational area, non-combinational area, black-box area]
# - area unit




data.extend([action_energy,energy_unit])
data.extend(pwr_flds)
data.extend([dyn_power_unit,leak_power_unit])
data.extend(area_flds)
data.append(area_unit)
data.extend(latency_flds)
data.append(latency_unit)
print(','.join([str(fld) for fld in data]))