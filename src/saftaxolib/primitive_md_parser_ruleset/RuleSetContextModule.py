# MetadataParser (primitive component) RuleSet

# - MetadataParser validation rules

# -- AssertPrimitiveMetadataParserSupportedInstantiation: MetadataParser instance must be supported

def assertPrimitiveMetadataParserAttributesAreSupported(obj):
    '''Assert that MetadataParser primitive instance is supported. Format must be in ['C','B'] or unknown'''
    fmt=obj.getAttributeById('format').getValue()
    print('Supported instantiation:',fmt)
    return fmt in ['C','B','R','U','?']


def predicateIsPrimitiveMetadataParser(obj):
    return type(obj).__name__ == 'Primitive' and obj.getCategory() == 'MetadataParser'

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
