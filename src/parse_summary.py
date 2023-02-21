import os
import parse_power, parse_area, parse_latency

header = ['name', \
          'action_energy', \
          'energy_unit', \
          'switch_power', \
          'int_power', \
          'leak_power', \
          'total_power', \
          'dyn_power_unit', \
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
          'latency_unit']

fn=input('')
if fn=='header':
    print(','.join(header))
    exit()

pwr_flds, dyn_power_unit, leak_power_unit = parse_power.parse_power(fn+'.power')
area_flds, area_unit = parse_area.parse_area(fn+'.area')
latency_flds, latency_unit = parse_latency.parse_latency(fn+'.latency')

# - float list of [absolute total area, combinational area, non-combinational area, black-box area]
# - area unit

# Compute derived action energy
assert(dyn_power_unit=='1mW')
assert(latency_unit=='ns')
total_power=pwr_flds[3]
clock_period=latency_flds[3]
action_energy=(total_power)*(clock_period) # (total_power*1e12/1000)*(clock_period/1e9)
energy_unit='pJ'

data = [os.path.split(fn)[-1]]
data.extend([action_energy,energy_unit])
data.extend(pwr_flds)
data.extend([dyn_power_unit,leak_power_unit])
data.extend(area_flds)
data.append(area_unit)
data.extend(latency_flds)
data.append(latency_unit)
print(','.join([str(fld) for fld in data]))