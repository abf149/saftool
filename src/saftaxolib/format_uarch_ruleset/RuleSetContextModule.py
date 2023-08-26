'''Format uarch RuleSet'''
from functools import reduce
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.notation import predicates as p_, \
                          attributes as a_, \
                          microarchitecture as m_, \
                          transform as t_                    
from util.notation.generators import boolean_operators as b_, \
                                     quantifiers as q_, \
                                     comparison as c_, \
                                     rules as r_

'''SAF, component and primitive imports'''
from saftaxolib.saf.FormatSAF import FormatSAF, isFMTSAF

from saftaxolib.microarchitecture.format.FormatUarch import FMTSAFtoUarch, \
                         newFMTUarchBufferStubNetlistFromFMTSAF, \
                         FormatUarch, \
                         fmt_uarch_instances, \
                         fmt_uarch_topologies

from saftaxolib.microarchitecture.format.MetadataParser import MetadataParser, md_parser_instances

''' Format microarchitecture'''

'''- SAF rewrite rules'''
''' -- ConcretizeArchitectureFormatSAFsToFormatUarches'''
''' --- concretize'''
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

''' --- predicate: object is an architecture with at least one format SAF'''
predicateIsArchitectureHasFormatSAF=b_.AND(p_.isArchitecture, \
                                           q_.anyForObjSAFs( \
                                                c_.equals( \
                                                    FormatSAF.name_, \
                                                    a_.getCategory \
                                                )
                                            )
                                    )

''' - Validation rules'''
''' -- AssertComponentFormatUarchAttributesAreSupported'''
''' --- assert supported instance '''
predicateIsComponentFormatUarch, \
assertComponentFormatUarchAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(fmt_uarch_instances,FormatUarch)

''' - Rewrite rules'''
''' -- TransformTopologicalHoleToPerRankMdParserTopology'''
''' --- transform supported instance topological hole to instance topology'''
predicateIsComponentIsFormatUarchHasTopologicalHole, \
transformTopologicalHoleToPerRankMdParserTopology = \
    r_.transformFillTopologyOfValidComponentOrPrimitiveMatchingCategoryRule(fmt_uarch_instances, \
                                                                            fmt_uarch_topologies, \
                                                                            FormatUarch)

'''MetadataParser microarchitecture primitive'''

''' - Validation rules'''
''' -- AssertPrimitiveMetadataParserAttributesAreSupported'''
''' --- assert supported instance'''
predicateIsPrimitiveMetadataParser, \
assertPrimitiveMetadataParserAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(md_parser_instances,MetadataParser)

