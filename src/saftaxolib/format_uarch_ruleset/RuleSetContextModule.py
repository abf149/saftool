# Format uarch RuleSet
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.notation import predicates as p_, attributes as a_, microarchitecture as m_, transform as t_
from util.notation.generators import boolean_operators as b_, quantifiers as q_, comparison as c_, rules as r_
from .saf import isFMTSAF, FMTSAFtoUarch
from .microarchitecture import newFMTUarchBufferStubNetlistFromFMTSAF, FormatUarch, MetadataParser, fmt_uarch_topologies
from .instances import fmt_uarch_instances, md_parser_instances
from functools import reduce

''' - Format SAF rewrite rules'''
''' -- ConcretizeArchitectureFormatSAFsToFormatUarches'''
''' --- concretization rule'''
concretizeArchitectureFormatSAFsToFormatUarches = \
    lambda obj: t_.transformSAFs(
                    t_.transformTopology(obj, \
                                         map(FMTSAFtoUarch, filter(isFMTSAF,obj.getSAFList())), \
                                         reduce(lambda x,y: x+y, map( \
                                                 newFMTUarchBufferStubNetlistFromFMTSAF, \
                                                 filter(isFMTSAF,obj.getSAFList())),[]), \
                                         append=True), \
                    filter(b_.NOT(isFMTSAF),obj.getSAFList()), append=False \
                )

''' --- predicate '''
'''Object is an architecture with at least one format SAF'''
predicateIsArchitectureHasFormatSAF=b_.AND(p_.isArchitecture, \
                                           q_.anyForObjSAFs( \
                                                c_.equals( \
                                                    m_.SAFFormat.name_, \
                                                    a_.getCategory \
                                                )
                                            )
                                    )

''' - Format uarch'''

''' - Format uarch validation rules'''
''' -- AssertComponentFormatUarchSupportedInstantiation: Format uarch instance must be supported'''
predicateIsComponentFormatUarch, \
assertComponentFormatUarchAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(fmt_uarch_instances,FormatUarch)

''' - Format uarch rewrite rules'''
''' -- TransformTopologicalHoleToPerRankMdParserTopology: For a format uarch with a topological hole, fill the hole with a topology comprising one MetadataParser primitive per traversed tensor rank at this buffer level'''

predicateIsComponentIsFormatUarchHasTopologicalHole, \
transformTopologicalHoleToPerRankMdParserTopology = \
    r_.transformFillTopologyOfValidComponentOrPrimitiveMatchingCategoryRule(fmt_uarch_instances, \
                                                                            fmt_uarch_topologies, \
                                                                            FormatUarch)

# - MetadataParser validation rules
# -- AssertPrimitiveMetadataParserSupportedInstantiation: MetadataParser instance must be supported
predicateIsPrimitiveMetadataParser, \
assertPrimitiveMetadataParserAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(md_parser_instances,MetadataParser)

#predicateIsPrimitiveMetadataParser=b_.AND(p_.isPrimitive,c_.equals(MetadataParser.name_,a_.getCategory))

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

