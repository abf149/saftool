# MetadataParser (primitive component) RuleSet

# - MetadataParser validation rules

# -- AssertPrimitiveMetadataParserSupportedInstantiation: MetadataParser instance must be supported

def assertPrimitiveMetadataParserAttributesAreSupported(obj):
    '''Assert that MetadataParser primitive instance is supported. Format must be in ['C','B'] or unknown'''
    fmt=obj.getAttributeById('format').getValue()
    return fmt in ['C','B','?']


def predicateIsPrimitiveMetadataParser(obj):
    return type(obj).__name__ == 'Primitive' and obj.getCategory() == 'MetadataParser'
