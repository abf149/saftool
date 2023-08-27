'''Position generator microarchitecture'''
from util.notation import microarchitecture as m_, transform as t_
from util.taxonomy.expressions import FormatType

'''Primitive definition'''
PositionGenerator = m_.PrimitiveCategory().name("PositionGenerator") \
                                          .attribute("format","format",FormatType.fromIdValue("format","?")) \
                                          .port_in("md_in","md","?",attr_reference="format") \
                                          .port_out("pos_out","pos","addr") \
                                          .generator(None)

'''Constructor'''
buildPositionGenerator = \
    lambda fmt_str: PositionGenerator.copy().set_attribute('format', \
                                                           FormatType.fromIdValue('format',fmt_str))

'''Supported instances'''
pgen_instances={ \
    "uncompressed":["U"], \
    "coordinate_payload":["C"], \
    "bitmask":["B"], \
    "run_length_encoding":["R"] \
}