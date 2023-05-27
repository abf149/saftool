latency_headers=['critical_path_length', \
                 'lvls_of_logic', \
                 'critical_path_slack', \
                 'critical_path_clock_latency', \
                 'total_negative_slack', \
                 'num_violating_paths', \
                 'worst_hold_violation', \
                 'total_hold_violation', \
                 'num_hold_violations', \
                 'latency_unit']

# Returns [cpl,lvls_of_logic,cps,cpc,tns,nvp,whv,thv,nhv], latency_unit
def parse_latency(fn):
    latency_unit='ns'
    lvls_of_logic=-1.0
    cpl=-1.0
    cps=-1.0
    cpc=-1.0
    tns=-1.0
    nvp=-1.0
    whv=-1.0
    thv=-1.0
    nhv=-1.0

    with open(fn) as f:
        lns=f.readlines()
        found_tpg=False
        for ln in lns:

            if 'Levels of Logic' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        lvls_of_logic=float(fld_str)
                    except:
                        pass

            if 'Critical Path Length' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        cpl=float(fld_str)
                    except:
                        pass

            if 'Critical Path Slack' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        cps=float(fld_str)
                    except:
                        pass

            if 'Critical Path Clk Period' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        cpc=float(fld_str)
                    except:
                        pass

            if 'Total Negative Slack' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        tns=float(fld_str)
                    except:
                        pass                                                                                

            if 'No. of Violating Paths' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        nvp=float(fld_str)
                    except:
                        pass

            if 'Worst Hold Violation' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        whv=float(fld_str)
                    except:
                        pass

            if 'Total Hold Violation' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        thv=float(fld_str)
                    except:
                        pass

            if 'No. of Hold Violations' in ln:
                flds_str=ln.strip().split()
                flds=[]
                for fld_str in flds_str:
                    try:
                        nhv=float(fld_str)
                    except:
                        pass

            if 'Timing Path Group' in ln:
                found_tpg=True

    return [cpl,lvls_of_logic,cps,cpc,tns,nvp,whv,thv,nhv], latency_unit