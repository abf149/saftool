'''Skipping uarch RuleSet'''
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
from saftaxolib.saf.SkippingSAF import SkippingSAF, isSkipSAF

'''
from saftaxolib.microarchitecture.format.FormatUarch import FMTSAFtoUarch, \
                         newFMTUarchBufferStubNetlistFromFMTSAF, \
                         FormatUarch, \
                         fmt_uarch_instances, \
                         fmt_uarch_topologies
'''

from saftaxolib.microarchitecture.skipping.SkippingUarch import SkippingUarch, \
                                                                skipping_uarch_instances, \
                                                                skipping_uarch_topologies

#from saftaxolib.microarchitecture.format.MetadataParser import MetadataParser, md_parser_instances

from saftaxolib.microarchitecture.skipping.Intersection import Intersection, intersection_instances

''' Skipping microarchitecture'''

'''- SAF rewrite rules (TODO)'''
''' -- ConcretizeArchitectureSkippingSAFsToSkippingUarches'''
''' --- concretize'''

'''
concretizeArchitectureSkippingSAFsToSkippingUarches = \
    lambda obj: t_.transformSAFs(
                    t_.transformTopology(obj, \
                                         map(FMTSAFtoUarch, filter(isFMTSAF,obj.getSAFList())), \
                                         reduce(lambda x,y: x+y, map( \
                                                 newFMTUarchBufferStubNetlistFromFMTSAF, \
                                                 filter(isFMTSAF,obj.getSAFList())),[]), \
                                         append=True), \
                    filter(b_.NOT(isFMTSAF),obj.getSAFList()), append=False \
                )
'''

''' --- predicate: object is an architecture with at least one format SAF'''
'''
predicateIsArchitectureHasFormatSAF=b_.AND(p_.isArchitecture, \
                                           q_.anyForObjSAFs( \
                                                c_.equals( \
                                                    FormatSAF.name_, \
                                                    a_.getCategory \
                                                )
                                            )
                                    )
'''

''' - Validation rules'''
''' -- AssertComponentSkippingUarchAttributesAreSupported'''
''' --- assert supported instance '''
predicateIsComponentSkippingUarch, \
assertComponentSkippingUarchAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(skipping_uarch_instances,SkippingUarch)

''' - Rewrite rules'''
''' -- TransformTopologicalHoleToPerRankMdParserTopology'''
''' --- transform supported instance topological hole to instance topology'''
predicateIsComponentIsSkippingUarchHasTopologicalHole, \
transformTopologicalHoleToIntersectionTopology = \
    r_.transformFillTopologyOfValidComponentOrPrimitiveMatchingCategoryRule(skipping_uarch_instances, \
                                                                            skipping_uarch_topologies, \
                                                                            SkippingUarch)

'''Intersection microarchitecture primitive'''

''' - Validation rules'''
''' -- AssertPrimitiveIntersectionAttributesAreSupported'''
''' --- assert supported instance'''
predicateIsIntersectionParser, \
assertPrimitiveIntersectionAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(intersection_instances,Intersection)

