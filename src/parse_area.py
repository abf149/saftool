# Returns:
# - float list of [absolute total area, combinational area, non-combinational area, black-box area]
# - area unit

area_headers=['Combinational_Area','Noncombinational_Area','Buf/Inv_Area','Total_Buffer_Area', \
                  'Total_Inverter_Area','Macro/Black_Box_Area','Net_Area']

def parse_area(fn):
    area_unit='um2'

    res={}

    with open(fn) as f:
        lns=f.readlines()

        found_area=False
        found_divider=False

        for ln in lns:
            
            if found_area:
                if found_divider:
                    if "----" in ln:
                        return res, area_unit
                    else:
                        ln_strip=ln.strip()
                        field_value=ln_strip.split(":") #(field,value)
                        fld=field_value[0].strip().replace(" ","_")
                        vl=float(field_value[1].strip())
                        res[fld]=vl
                else:
                    if "----" in ln:
                        found_divider=True
            else:
                if ln.strip()=="Area":
                    found_area=True