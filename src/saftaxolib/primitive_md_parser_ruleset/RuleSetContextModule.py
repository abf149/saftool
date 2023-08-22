# MetadataParser (primitive component) RuleSet
import util.notation.predicates as p_
import util.notation.generators.boolean_operators as b_
import util.notation.generators.comparison as c_
import util.notation.microarchitecture as m_
import util.notation.attributes as a_
from util.taxonomy.expressions import FormatType

MetadataParser = m_.PrimitiveCategory().name("MetadataParser") \
                   .port_in("md_in","md","?") \
                   .port_out("at_bound_out","pos","addr") \
                   .attribute("format","format",FormatType.fromIdValue("format","?")) \
                   .generator(None)

# - MetadataParser validation rules

# -- AssertPrimitiveMetadataParserSupportedInstantiation: MetadataParser instance must be supported

def assertPrimitiveMetadataParserAttributesAreSupported(obj):
    '''Assert that MetadataParser primitive instance is supported. Format must be in ['C','B'] or unknown'''
    fmt=obj.getAttributeById('format').getValue()
    return fmt in ['C','B','R','U','?']

predicateIsPrimitiveMetadataParser=b_.AND(p_.isPrimitive,c_.equals(MetadataParser.name_,a_.getCategory))

# - MetadataParser rewrite rules

def transformUnknownAttributeTypeFromInterfaceType(obj):
    attribute_unknown=obj.getAttributeById('format').isUnknown()

    interface_type=obj.getPortById('md_in').getFormatType().getValue()

    # TODO: make a real read/modify/write for attributes
    atts=obj.getAttributes()
    for idx in range(len(atts)):
        if type(atts[idx]).__name__=='FormatType' and atts[idx].getId()=='format':
            atts[idx].setValue(interface_type)
    obj.setAttributes(atts)
    return obj



def predicateIsPrimitiveMetadataParserHasUnknownAttributeTypeAndKnownInterfaceType(obj):
    return predicateIsPrimitiveMetadataParser(obj) and (not obj.getPortById('md_in').getFormatType().isUnknown()) and obj.getAttributeById('format').isUnknown()
