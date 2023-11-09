'''Gating uarch RuleSet'''             
from util.notation.generators import rules as r_

import saflib.microarchitecture.taxo.TaxoRegistry as tr_

pgen_dict=tr_.getPrimitive("FillGate")
FillGate=pgen_dict["description"]
fill_gate_instances=pgen_dict["instances"]


'''Primitive imports'''
#from saflib.microarchitecture.taxo.gating.FillGate import FillGate, fill_gate_instances

'''FillGate microarchitecture primitive'''

''' - Validation rules'''
''' -- AssertPrimitiveFillGateAttributesAreSupported'''
''' --- assert supported instance'''
predicateIsFillGate, \
assertPrimitiveFillGateAttributesAreSupported = \
    r_.isValidComponentOrPrimitiveMatchingCategoryRule(fill_gate_instances,FillGate)