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
from saflib.saf.SkippingSAF import SkippingSAF, isSkipSAF
import saflib.microarchitecture.TaxoRegistry as tr_

skipping_uarch_dict=tr_.getComponent("SkippingUarch")
SkippingUarch=skipping_uarch_dict["description"]
skipping_uarch_instances=skipping_uarch_dict["instances"]
skipping_uarch_topologies=skipping_uarch_dict["topologies"]

from saflib.saf.microarchitecture_from_saf.skipping.SkippingUarch import SkipSAFtoUarch, \
                                                   newSkipUarchBufferStubNetlistFromSkipSAF

ilf_dict=tr_.getPrimitive("IntersectionLeaderFollower")
IntersectionLeaderFollower=ilf_dict["description"]
intersection_lf_instances=ilf_dict["instances"]

''' Skipping microarchitecture'''

'''- SAF rewrite rules'''
''' -- ConcretizeArchitectureSkippingSAFsToSkippingUarches'''
''' --- concretize'''
concretizeArchitectureSkippingSAFsToSkippingUarches = \
    lambda obj: t_.transformSAFs(
                    t_.transformTopology(obj, \
                                         map(SkipSAFtoUarch, filter(isSkipSAF,obj.getSAFList())), \
                                         reduce(lambda x,y: x+y, map( \
                                                 newSkipUarchBufferStubNetlistFromSkipSAF, \
                                                 filter(isSkipSAF,obj.getSAFList())),[]), \
                                         append=True), \
                    filter(b_.NOT(isSkipSAF),obj.getSAFList()), append=False \
                )


''' --- predicate: object is an architecture with at least one Skipping SAF'''
predicateIsArchitectureHasSkippingSAF=b_.AND(p_.isArchitecture, \
                                           q_.anyForObjSAFs( \
                                                c_.equals( \
                                                    SkippingSAF.name_, \
                                                    a_.getCategory \
                                                )
                                            )
                                    )

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
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(intersection_lf_instances,IntersectionLeaderFollower)

