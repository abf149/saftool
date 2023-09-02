'''Position generator uarch RuleSet'''             
from util.notation.generators import rules as r_

'''Primitive imports'''
from saflib.microarchitecture.taxo.address_primitives.PositionGenerator \
    import PositionGenerator as Pgen, pgen_instances

'''Position generator microarchitecture primitive'''

''' - Validation rules'''
''' -- AssertPrimitivePgenAttributesAreSupported'''
''' --- assert supported instance'''
predicateIsPgen, \
assertPrimitivePgenAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(pgen_instances,Pgen)