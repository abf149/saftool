'''Format microarchitecture'''
from util.notation import microarchitecture as m_, transform as t_
from util.taxonomy.expressions import FormatType

'''Primitive definition'''
MetadataParser = m_.PrimitiveCategory().name("MetadataParser") \
                   .attribute("format","format",FormatType.fromIdValue("format","?")) \
                   .port_in("md_in","md","?",attr_reference="format") \
                   .port_out("at_bound_out","flag","none") \
                   .generator(None)

'''Constructor'''
buildMetadataParser = \
    lambda fmt_str: MetadataParser.copy().set_attribute('format', \
                                                           FormatType.fromIdValue('format',fmt_str))

'''Supported instances'''
md_parser_instances={ \
    "uncompressed":["U"], \
    "coordinate_payload":["C"], \
    "bitmask":["B"], \
    "run_length_encoding":["R"] \
}