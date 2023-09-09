'''Base SAFInfer RuleSet'''
from util.notation.generators import quantifiers as q_, boolean_operators as b_
from util.notation import attributes as a_, objects as o_, predicates as p_, transform as t_
from util.taxonomy.expressions import FormatType

''' Topology validation rules'''
''' - AssertNetHasConsistentPortNetType: all ports connected by a Net should have a consistent NetType'''
'''
predicateHasConsistentPortNetTypes = p_.isComponentOrArchitectureHasNets
assertHasConsistentPortNetTypes = q_.forObjNetsForNetPorts("all","same",a_.getNetType)
'''
'''  - AssertNetHasConsistentPortFormatType: all ports connected by a Net should have a consistent FormatType'''
'''
predicateNetHasConsistentPortFormatType = p_.isComponentOrArchitectureHasNets
assertNetHasConsistentPortFormatType = q_.forObjNetsForNetPorts("all", \
                                                                "same", \
                                                                a_.getFormat, \
                                                                comparator = FormatType.compareFormatTypes
                                                               )
'''
'''- AssertIsComponentOrArchitectureHasTopology: no topological holes in design'''
'''
predicateIsComponentOrArchitectureHasTopology = p_.isComponentOrArchitecture
checkIsComponentOrArchitectureHasTopology = b_.NOT(p_.hasTopologicalHole)
'''

''' Topology rewrite rules'''
''' - TransformUnknownPortTypesOnNetsWithKnownTypesToKnownType: infer unknown port types on nets where some port types are known'''

predicateUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType = b_.AND( \
                                                                            p_.isComponentOrArchitectureHasNets, \
                                                                            p_.canFloodNetFormatToChildPorts
                                                                        )
transformUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType = t_.transformFloodNetFormatToChildPorts

''' Topology completion rules'''
''' - CheckComponentHasNoTopologicalHoles: the component should contain no topological holes'''

predicateComponentHasNoTopologicalHoles = p_.isComponent
checkComponentHasNoTopologicalHoles = b_.NOT(p_.hasTopologicalHole)

''' - CheckComponentHasNoUnknownInterfaceTypes: the component's interface ports should all have known types'''
'''
predicateComponentHasNoUnknownInterfaceTypes = p_.isComponentOrPrimitive
checkComponentHasNoUnknownInterfaceTypes = b_.NOT(q_.anyForObjPorts(p_.isPortWithUnknownFormat))
'''
''' - CheckComponentHasNoUnknownAttributeTypes: the component's attributes should all have known types'''
'''
predicateComponentHasNoUnknownAttributeTypes = p_.isComponentOrPrimitive
checkComponentHasNoUnknownAttributeTypes = b_.NOT(q_.anyForObjAttributes(p_.isUnknownFormatAttribute))
'''

''' - TransformSetUnknownAttributeFromKnownInterfaceTypeReferencingAttribute:
      Allow component attributes to be inferred from interface type
'''
'''
transformSetUnknownAttributeFromKnownInterfaceTypeReferencingAttribute = \
    lambda obj: t_.transformObjAttribute(obj, \
        *(a_.getKnownInterfaceTypeReferencingUnknownAttribute(obj)[1:]))

predicateIsPrimitiveOrComponentHasUnknownAttributeTypeAndKnownInterfaceTypeReferencingAttribute = \
    b_.AND(b_.OR(p_.isPrimitive, \
                 p_.isComponent), \
           p_.hasKnownInterfaceTypeReferencingUnknownAttribute)
'''

''' - TransformSetUnknownInterfaceTypeFromReferencedKnownAttribute:
      Allow interface type to be inferred from component attribute
'''
'''
transformSetUnknownInterfaceTypeFromReferencedKnownAttribute = \
    lambda obj: t_.transformObjInterfacePort(obj, \
        *(a_.getKnownAttributeTypeReferencedByPortWithUnknownAttribute(obj)[1:]))

predicateIsPrimitiveOrComponentHasUnknownInterfaceTypeReferencingKnownAttribute = \
    b_.AND(b_.OR(p_.isPrimitive, \
                 p_.isComponent), \
           p_.hasKnownAttributeTypeReferencedByPortWithUnknownAttribute)
'''