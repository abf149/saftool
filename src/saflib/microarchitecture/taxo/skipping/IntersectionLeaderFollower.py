'''Intersection unit microarchitecture'''
from util.notation import microarchitecture as m_
from util.taxonomy.expressions import FormatType

'''Primitive definition'''
IntersectionLeaderFollower = m_.PrimitiveCategory().name("IntersectionLeaderFollower") \
                                                   .attribute("format_leader","format",FormatType.fromIdValue("format","?")) \
                                                   .attribute("strategy","string","none") \
                                                   .port_in("md_in_leader","md","?",attr_reference="format_leader") \
                                                   .port_out("md_out","md","?",attr_reference="format_leader") \
                                                   .generator(None)

'''Constructor'''
buildIntersectionLeaderFollower = \
    lambda f_str_leader,strategy: IntersectionLeaderFollower.copy().set_attribute('format_leader', \
                                                                                    FormatType.fromIdValue('format_leader',f_str_leader)) \
                                                                                .set_attribute('strategy', \
                                                                                    strategy)

'''Supported instances'''
intersection_instances={ \
    "unc_lf_none":["U","none"], \
    "cp_lf_none":["C","none"], \
    "b_lf_none":["B","none"], \
    "r_lf_none":["R","none"]
}