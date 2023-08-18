'''Base SAFInfer RuleSet'''
from util.notation.generators import quantifiers as q_, boolean_operators as b_
from util.notation import attributes as a_, objects as o_, predicates as p_, transform as t_
from util.taxonomy.expressions import FormatType

''' Topology validation rules'''
''' - AssertNetHasConsistentPortNetType: all ports connected by a Net should have a consistent NetType'''
predicateHasConsistentPortNetTypes = p_.isComponentOrArchitectureHasNets
assertHasConsistentPortNetTypes = q_.forObjNetsForNetPorts("all","same",a_.getNetType)
'''  - AssertNetHasConsistentPortFormatType: all ports connected by a Net should have a consistent FormatType'''
predicateNetHasConsistentPortFormatType = p_.isComponentOrArchitectureHasNets
assertNetHasConsistentPortFormatType = q_.forObjNetsForNetPorts("all", \
                                                                "same", \
                                                                a_.getFormat, \
                                                                comparator = FormatType.compareFormatTypes
                                                               )

''' Topology rewrite rules'''
''' - TransformUnknownPortTypesOnNetsWithKnownTypesToKnownType: infer unknown port types on nets where some port types are known'''
predicateUnknownPortTypesOnNetsWithKnownTypesToKnownType = b_.AND(
                                                                  p_.isComponentOrArchitectureHasNets,
                                                                  q_.anyForObjPorts(p_.isPortWithUnknownFormat)
                                                                 )
transformUnknownPortTypesOnNetsWithKnownTypesToKnownType = t_.transformFloodNetFormatToObjPorts
''' 
    - TransformUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType: infer unknown child component port types on nets 
      where some port types are known
'''
predicateUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType = b_.AND( \
                                                                            p_.isComponentOrArchitectureHasNets, \
                                                                            q_.anyForObjComponents( \
                                                                                q_.anyForObjPorts( \
                                                                                p_.isPortWithUnknownFormat
                                                                                )
                                                                            )
                                                                        )
transformUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType = t_.transformFloodNetFormatToChildPorts

''' Topology completion rules'''
''' - CheckComponentHasNoTopologicalHoles: the component should contain no topological holes'''
predicateComponentHasNoTopologicalHoles = p_.isComponent
checkComponentHasNoTopologicalHoles = b_.NOT(p_.hasTopologicalHole)
''' - CheckComponentHasNoUnknownInterfaceTypes: the component's interface ports should all have known types'''
predicateComponentHasNoUnknownInterfaceTypes = p_.isComponentOrPrimitive
checkComponentHasNoUnknownInterfaceTypes = b_.NOT(q_.anyForObjPorts(p_.isPortWithUnknownFormat))
''' - CheckComponentHasNoUnknownAttributeTypes: the component's attributes should all have known types'''
predicateComponentHasNoUnknownAttributeTypes = p_.isComponentOrPrimitive
checkComponentHasNoUnknownAttributeTypes = b_.NOT(q_.anyForObjAttributes(p_.isUnknownFormatAttribute))