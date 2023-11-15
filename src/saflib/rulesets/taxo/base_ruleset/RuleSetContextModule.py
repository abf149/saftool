'''Base SAFInfer RuleSet'''
from util.notation.generators import quantifiers as q_, boolean_operators as b_
from util.notation import attributes as a_, objects as o_, predicates as p_, transform as t_
import saflib.microarchitecture.TaxoRegistry as tr_
from util.notation.generators import rules as r_
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
'''- CheckIsComponentOrArchitectureHasTopology: no topological holes in design'''
predicateIsComponentOrArchitectureHasTopology = p_.isComponentOrArchitecture
checkIsComponentOrArchitectureHasTopology = b_.NOT(p_.hasTopologicalHole)

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
predicateComponentHasNoUnknownInterfaceTypes = p_.isComponentOrPrimitive
checkComponentHasNoUnknownInterfaceTypes = b_.NOT(q_.anyForObjPorts(p_.isPortWithUnknownFormat))
''' - CheckComponentHasNoUnknownAttributeTypes: the component's attributes should all have known types'''
predicateComponentHasNoUnknownAttributeTypes = p_.isComponentOrPrimitive
checkComponentHasNoUnknownAttributeTypes = b_.NOT(q_.anyForObjAttributes(b_.OR(p_.isUnknownFormatAttribute, \
                                                                               p_.isUnknownStringAttribute)))

''' - TransformSetUnknownAttributeFromKnownInterfaceTypeReferencingAttribute:
      Allow component attributes to be inferred from interface type
'''
transformSetUnknownAttributeFromKnownInterfaceTypeReferencingAttribute = \
    lambda obj: t_.transformObjAttribute(obj, \
        *(a_.getKnownInterfaceTypeReferencingUnknownAttribute(obj)[1:]))

predicateIsPrimitiveOrComponentHasUnknownAttributeTypeAndKnownInterfaceTypeReferencingAttribute = \
    b_.AND(b_.OR(p_.isPrimitive, \
                 p_.isComponent), \
           p_.hasKnownInterfaceTypeReferencingUnknownAttribute)

''' - TransformSetUnknownInterfaceTypeFromReferencedKnownAttribute:
      Allow interface type to be inferred from component attribute
'''
transformSetUnknownInterfaceTypeFromReferencedKnownAttribute = \
    lambda obj: t_.transformObjInterfacePort(obj, \
        *(a_.getKnownAttributeTypeReferencedByPortWithUnknownAttribute(obj)[1:]))

predicateIsPrimitiveOrComponentHasUnknownInterfaceTypeReferencingKnownAttribute = \
    b_.AND(b_.OR(p_.isPrimitive, \
                 p_.isComponent), \
           p_.hasKnownAttributeTypeReferencedByPortWithUnknownAttribute)

'''Primitive validation rules'''
''' - Validation rules'''
''' -- AssertPrimitiveAttributesAreSupported'''
def predicateIsMicroarchitecturePrimitive(obj):
    return p_.isPrimitive(obj) and obj.getCategory()!="BufferStub"
def getPrimitiveCategoryAndSupportedInstances(obj):
    category_str=obj.getCategory()
    ilf_dict=tr_.getPrimitive(category_str)
    category=ilf_dict["description"]
    supported_instances=ilf_dict["instances"]
    return category,supported_instances

def assertPrimitiveAttributesAreSupported(obj):
    category,supported_instances= \
        getPrimitiveCategoryAndSupportedInstances(obj)
    _,valid=r_.isValidComponentOrPrimitiveMatchingCategoryRule \
                (supported_instances,category)
    return valid(obj)

'''Component validation rules'''
''' - Validation rules'''
''' -- AssertComponentAttributesAreSupported'''
def predicateIsMicroarchitectureComponent(obj):
    return p_.isComponent(obj)
def getComponentCategoryAndSupportedInstances(obj):
    category_str=obj.getCategory()
    ilf_dict=tr_.getComponent(category_str)
    category=ilf_dict["description"]
    supported_instances=ilf_dict["instances"]
    return category,supported_instances

def assertComponentAttributesAreSupported(obj):
    category,supported_instances= \
        getComponentCategoryAndSupportedInstances(obj)
    _,valid=r_.isValidComponentOrPrimitiveMatchingCategoryRule \
                     (supported_instances,category)
    return valid(obj)

'''Component rewrite rules'''
def predicateIsComponentHasTopologicalHole(obj):
    return p_.isComponent(obj) and (not p_.isArchitecture(obj)) \
           and p_.hasTopologicalHole(obj)
def getComponentCategoryAndSupportedInstancesAndTopologies(obj):
    category_str=obj.getCategory()
    ilf_dict=tr_.getComponent(category_str)
    category=ilf_dict["description"]
    supported_instances=ilf_dict["instances"]
    topologies=ilf_dict["topologies"]
    return category,supported_instances,topologies

def transformTopologicalHoleToIntersectionTopology(obj):
    category, \
    supported_instances, \
    topologies=getComponentCategoryAndSupportedInstancesAndTopologies(obj)
    _,xform=r_.transformFillTopologyOfValidComponentOrPrimitiveMatchingCategoryRule(supported_instances, \
                                                                                    topologies, \
                                                                                    category)
    x=xform(obj)
    #print(obj.getId())
    #print(obj.getCategory())
    #print(obj)
    return x