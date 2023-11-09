'''Intersection unit microarchitecture'''
from util.notation import microarchitecture as m_
from util.taxonomy.expressions import FormatType

'''Primitive definition'''
IntersectionBidirectional = m_.PrimitiveCategory().name("IntersectionBidirectional") \
                                                  .attribute("format_0","format",FormatType.fromIdValue("format","?")) \
                                                  .attribute("format_1","format",FormatType.fromIdValue("format","?")) \
                                                  .attribute("strategy","string","none") \
                                                  .port_in("md_in_0","md","?",attr_reference="format_leader") \
                                                  .port_in("md_in_1","md","?",attr_reference="format_follower") \
                                                  .port_out("md_out","md","?",attr_reference="format_leader") \
                                                  .generator(None)

'''Constructor'''
buildIntersectionBidirectional = \
    lambda f_str_leader,f_str_follower,strategy: IntersectionBidirectional.copy().set_attribute('format_leader', \
                                                                                    FormatType.fromIdValue('format_leader',f_str_leader)) \
                                                                                .set_attribute('format_follower', \
                                                                                    FormatType.fromIdValue('format_follower',f_str_follower)) \
                                                                                .set_attribute('strategy', \
                                                                                    strategy)

'''Supported instances'''
intersection_instances={ \
    "unc_bd_none":["U","U","bidirectional","none"], \
    "cp_bd_none":["C","C","bidirectional","none"], \
    "cp_bd_opskip":["C","C","bidirectional","operand_skip"], \
    "b_bd_none":["B","B","bidirectional","none"], \
    "r_bd_none":["R","R","bidirectional","none"]
}