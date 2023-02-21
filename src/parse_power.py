# Returns:
# - float list of [switch power, int power, leak power, total power]
# - dynamic power unit
# - leakage power unit
def parse_power(fn):
    dyn_power_unit=''
    leak_power_unit=''

    with open(fn) as f:
        lns=f.readlines()
        found_hierarchy=False
        found_divider=False
        for ln in lns:
            if 'Dynamic Power Units' in ln:
                flds_str=ln.split()
                dyn_power_unit=flds_str[4]
            
            if 'Leakage Power Units' in ln:
                flds_str=ln.split()
                leak_power_unit=flds_str[4]

            if found_divider:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        flds.append(float(fld_str))
                    except:
                        pass
                return flds[0:-1], dyn_power_unit, leak_power_unit
            if found_hierarchy and '-' in ln:
                found_divider=True
            if 'Hierarchy' in ln:
                found_hierarchy=True