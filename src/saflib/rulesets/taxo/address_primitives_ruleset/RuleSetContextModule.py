'''Position generator uarch RuleSet'''             
from util.notation.generators import rules as r_

'''Primitive imports'''
''' - Validation rules'''
''' -- AssertPrimitivePgenAttributesAreSupported'''
''' --- assert supported instance'''

import saflib.microarchitecture.taxo.TaxoRegistry as tr_

pgen_dict=tr_.getPrimitive("PositionGenerator")

predicateIsPgen, \
assertPrimitivePgenAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(pgen_dict['instances'], \
                                                       pgen_dict['description'])