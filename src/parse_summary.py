import os
import parse_power, parse_area, parse_latency
from parse_power import power_headers
from parse_area import area_headers
from parse_latency import latency_headers

# Build csv column headers
header = ['name'] # component name
header.extend(power_headers)
header.extend(['dyn_power_unit','leak_power_unit'])
header.extend(area_headers)
header.append('area_unit')
header.extend(latency_headers)
header.append('latency_unit')

# Base file name
fn=input('')
if fn=='header':
    print(','.join(header))
    exit()

# Power values
power_breakdown_flat, power_headers, dyn_power_unit, leak_power_unit = parse_power.parse_power(fn+'.power')
# Compute derived action energy
assert(dyn_power_unit=='1mW')

#total_power=pwr_flds[3]
#clock_period=latency_flds[3]
#action_energy=(total_power)*(clock_period) # (total_power*1e12/1000)*(clock_period/1e9)
#energy_unit='pJ'


area_breakdown, area_unit = parse_area.parse_area(fn+'.area')
latency_breakdown, latency_unit = parse_latency.parse_latency(fn+'.latency')
assert(latency_unit=='ns')

#raise ValueError(str(breakdown))

# - float list of [absolute total area, combinational area, non-combinational area, black-box area]
# - area unit

#breakdown_flat, power_headers, dyn_power_unit, leak_power_unit

# Populate CSV data
data = [os.path.split(fn)[-1]] # name
#data.extend([action_energy,energy_unit])
data.extend([power_breakdown_flat[fld] for fld in power_headers])
data.extend([dyn_power_unit,leak_power_unit])
data.extend([area_breakdown[fld] for fld in area_headers])
data.append(area_unit)
data.extend([str(l) for l in latency_breakdown])
data.append(latency_unit)
print(','.join([str(fld) for fld in data]))