'''Base SAFInfer RuleSet'''
from core.notation.generators import quantifiers as q_, boolean_operators as b_
from core.notation import attributes as a_, objects as o_, predicates as p_, transform as t_
import saflib.microarchitecture.TaxoRegistry as tr_
from core.notation.generators import rules as r_
from core.taxonomy.expressions import FormatType

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
    # Permissive match - "unknowns" (?) and wildcards match
    category,supported_instances= \
        getPrimitiveCategoryAndSupportedInstances(obj)
    _,valid=r_.isValidComponentOrPrimitiveMatchingCategoryRule \
                (supported_instances,category,strict=False)
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
    # Permissive match - "unknowns" (?) and wildcards match
    category,supported_instances= \
        getComponentCategoryAndSupportedInstances(obj)
    _,valid=r_.isValidComponentOrPrimitiveMatchingCategoryRule \
                     (supported_instances,category,strict=False)
    return valid(obj)

def assertPrimitiveAttributesStrictMatch(obj):
    category,supported_instances= \
        getPrimitiveCategoryAndSupportedInstances(obj)
    _,valid=r_.isValidComponentOrPrimitiveMatchingCategoryRule \
                     (supported_instances,category,strict=True)
    return valid(obj)

def assertComponentAttributesStrictMatch(obj):
    category,supported_instances= \
        getComponentCategoryAndSupportedInstances(obj)
    _,valid=r_.isValidComponentOrPrimitiveMatchingCategoryRule \
                     (supported_instances,category,strict=True)
    return valid(obj)

'''Component rewrite rules'''

# Topology inference given known valid attributes
def predicateIsComponentHasTopologicalHoleHasValidAttributesWithNoUnknowns(obj):
    return p_.isComponent(obj) and (not p_.isArchitecture(obj)) \
           and p_.hasTopologicalHole(obj) \
           and assertComponentAttributesStrictMatch(obj)
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

'''Component *or* primitive rules'''

def predicateIsComponentOrPrimitiveNotArchitectureHasUnknownsIsSupportedWithOnePossibility(obj):

    category = None
    supported_instances = None

    # Check that component is not architecture
    if p_.isArchitecture(obj):
        return False

    # Check that primitive is not BufferStub
    if p_.isBufferStub(obj):
        return False

    # Check that component only matches with unknowns wild
    if p_.isComponent(obj):
        # False if no soft match (unknowns wild)
        if not assertComponentAttributesAreSupported(obj):
            return False
        # False if hard match (already determined)
        if assertComponentAttributesStrictMatch(obj):
            return False

        category,supported_instances = \
            getComponentCategoryAndSupportedInstances(obj)

    if p_.isPrimitive(obj):
        # False if no soft match (unknowns wild)
        if not assertPrimitiveAttributesAreSupported(obj):
            return False
        # False if hard match (already determined)
        if assertPrimitiveAttributesStrictMatch(obj):
            return False
        
        category,supported_instances = \
            getPrimitiveCategoryAndSupportedInstances(obj)

    # Check that there is only one possible supported instance
    specialization_list = r_.findAllInstancesPartiallyMatchingObjectAttributes(obj.getAttributes(),supported_instances,category.attributes_)

    if len(specialization_list) == 1:
        return True

    # Otherwise...
    return False

def transformToSinglePossibility(obj):

    category = None
    supported_instances = None

    if p_.isComponent(obj):
        category,supported_instances = \
            getComponentCategoryAndSupportedInstances(obj)

    if p_.isPrimitive(obj):
        category,supported_instances = \
            getPrimitiveCategoryAndSupportedInstances(obj)

    specialization_list = r_.findAllInstancesPartiallyMatchingObjectAttributes(obj.getAttributes(),supported_instances,category.attributes_)
    assert(len(specialization_list) == 1) # Should have already been checked
    target_specialization = specialization_list[0]

    # Check and populate those attributes which are unknown
    attrs_=obj.getAttributes()

    for idx in range(len(attrs_)):
        if attrs_[idx] == "?":
            attrs_[idx] = target_specialization['inst_attr'][idx]
    obj.setAttributes(attrs_)

    return obj

