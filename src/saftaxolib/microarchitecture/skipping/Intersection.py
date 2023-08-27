'''Intersection unit microarchitecture'''
from util.notation import microarchitecture as m_
from util.taxonomy.expressions import FormatType

'''Primitive definition'''
Intersection = m_.PrimitiveCategory().name("Intersection") \
                                     .attribute("format_leader","format",FormatType.fromIdValue("format","?")) \
                                     .attribute("format_follower","format",FormatType.fromIdValue("format","?")) \
                                     .attribute("direction","string","bidirectional") \
                                     .attribute("strategy","string","none") \
                                     .port_in("md_in_leader","md","?",attr_reference="format_leader") \
                                     .port_in("md_in_follower","md","?",attr_reference="format_follower") \
                                     .port_out("md_out","md","?") \
                                     .generator(None)

'''Constructor'''
buildIntersection = \
    lambda f_str_leader,f_str_follower,direction,strategy: Intersection.copy().set_attribute('format_leader', \
                                                                                    FormatType.fromIdValue('format_leader',f_str_leader)) \
                                                                                .set_attribute('format_follower', \
                                                                                    FormatType.fromIdValue('format_follower',f_str_follower)) \
                                                                                .set_attribute('direction', \
                                                                                    direction) \
                                                                                .set_attribute('strategy', \
                                                                                    strategy)

'''Supported instances'''
intersection_instances={ \
    "unc_bd_none":["U","U","bidirectional","none"], \
    "unc_lf_none":["U","U","leader_follower","none"], \
    "cp_bd_none":["C","C","bidirectional","none"], \
    "cp_bd_opskip":["C","C","bidirectional","operand_skip"], \
    "cp_lf_none":["C","C","leader_follower","none"], \
    "b_bd_none":["B","B","bidirectional","none"], \
    "b_lf_none":["B","B","leader_follower","none"], \
    "r_bd_none":["R","R","bidirectional","none"], \
    "r_lf_none":["R","R","leader_follower","none"]
}