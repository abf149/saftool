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
'''- AssertIsComponentOrArchitectureHasTopology: no topological holes in design'''
predicateIsComponentOrArchitectureHasTopology = p_.isComponentOrArchitecture
checkIsComponentOrArchitectureHasTopology = b_.NOT(p_.hasTopologicalHole)

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

transformSetUnknownAttributeFromKnownInterfaceTypeReferencingAttribute = \
    lambda obj: t_.transformObjAttribute(obj, \
        *(a_.getKnownInterfaceTypeReferencingUnknownAttribute(obj)[1:]))

predicateIsPrimitiveOrComponentHasUnknownAttributeTypeAndKnownInterfaceTypeReferencingAttribute = \
    b_.AND(b_.OR(p_.isPrimitive, \
                 p_.isComponent), \
           p_.hasKnownInterfaceTypeReferencingUnknownAttribute)

# - MetadataParser rewrite rules
'''
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
'''

#predicateIsPrimitiveOrComponent

'''
predicateIsPrimitiveMetadataParserHasUnknownAttributeTypeAndKnownInterfaceType = \
    b_.AND(p_.isPrimitive, \
           lambda obj: p_.isCategory(obj,"MetadataParser"), \
           b_.NOT(lambda obj: obj.getPortById('md_in').getFormatType().isUnknown()), \
           lambda obj: obj.getAttributeById('format').isUnknown())
'''

'''
def predicateIsPrimitiveMetadataParserHasUnknownAttributeTypeAndKnownInterfaceType(obj):
    return predicateIsPrimitiveMetadataParser(obj) and (not obj.getPortById('md_in').getFormatType().isUnknown()) and obj.getAttributeById('format').isUnknown()
'''