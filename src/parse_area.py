# Returns:
# - float list of [absolute total area, combinational area, non-combinational area, black-box area]
# - area unit
def parse_area(fn):
    area_unit='um2'

    with open(fn) as f:
        lns=f.readlines()
        found_hierarchy=False
        found_divider=False
        for ln in lns:

            if found_divider:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        flds.append(float(fld_str))
                    except:
                        pass
                res = [flds[0]]
                res.extend(flds[2:])
                return res, area_unit

            if found_hierarchy and '-' in ln:
                found_divider=True
            if 'Hierarchical' in ln:
                found_hierarchy=True