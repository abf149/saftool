'''Gating uarch RuleSet'''             
from util.notation.generators import rules as r_

'''Primitive imports'''
from saflib.microarchitecture.taxo.gating.FillGate import FillGate, fill_gate_instances

'''FillGate microarchitecture primitive'''

''' - Validation rules'''
''' -- AssertPrimitiveFillGateAttributesAreSupported'''
''' --- assert supported instance'''
predicateIsFillGate, \
assertPrimitiveFillGateAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(fill_gate_instances,FillGate)