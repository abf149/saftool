'''SAF representation format metadata parser'''
import util.notation.microarchitecture as m_

FormatUarch = m_.ComponentCategory() \
                .name("FormatUarch") \
                .attribute("fibertree","fibertree","?") \
                .port_in_generator("md_in$x","format",["$v","?"],"fibertree") \
                .port_out_generator("at_bound_out$x","addr","pos","fibertree")