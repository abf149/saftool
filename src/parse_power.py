import os

if not os.getenv("SPHINX_BUILD"):

    fld_names=['internal_power','switching_power','leakage_power','total_power']
    cat_names=['io_pad','memory','black_box','clock_network','register','sequential','combinational']
    power_headers=[]

    for ctn in cat_names:
        for fdn in fld_names:
            power_headers.append(ctn+"_"+fdn)


    # Returns:
    # - float list of [switch power, int power, leak power, total power]
    # - dynamic power unit
    # - leakage power unit
    def parse_power(fn):
        dyn_power_unit=''
        leak_power_unit=''
        breakdown={}

        with open(fn) as f:
            lns=f.readlines()
            found_hierarchy=False
            found_divider=False
            for ln in lns:

                if ('Total' in ln) and found_divider:
                    breakdown_flat={}
                    for ctn in cat_names:
                        for fdn in fld_names:
                            breakdown_flat[ctn+"_"+fdn]=breakdown[ctn][fdn]

                    return breakdown_flat, power_headers, dyn_power_unit, leak_power_unit

                if 'Dynamic Power Units' in ln:
                    flds_str=ln.split()
                    dyn_power_unit=flds_str[4]
                
                if 'Leakage Power Units' in ln:
                    flds_str=ln.split()
                    leak_power_unit=flds_str[4]

                if found_divider and not('--' in ln):
                    flds_str=ln.strip().split()
                    idxs=[0,1,2,3,4]
                    flds=[]
                    for idx in idxs:
                        flds.append(flds_str[idx])
                    num_flds=len(fld_names)                    
                    value_flds=flds[1:(num_flds+1)]
                    breakdown[flds[0]] = {fld_names[idx]:float(value_flds[idx]) for idx in range(num_flds)}

                if found_hierarchy and '--' in ln:
                    found_divider=True
                if 'Power Group' in ln:
                    found_hierarchy=True