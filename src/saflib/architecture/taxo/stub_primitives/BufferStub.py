import util.notation.microarchitecture as m_

BufferStub = m_.PrimitiveCategory().name("BufferStub") \
                                   .port_out("md_out$x","md","$v") \
                                   .port_in("at_bound_in$x","flag","none") \
                                   .port_in("pos_in$x","pos","addr") \
                                   .attribute("fibertree",["fibertree"],[None]) \
                                   .generator("fibertree")