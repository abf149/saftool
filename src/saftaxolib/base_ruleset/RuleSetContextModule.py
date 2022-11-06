# General topology rules

from util.taxonomy.expressions import FormatType

# - Topology validation rules

# -- AssertNetHasConsistentPortNetType: all ports connected by a Net should have a consistent NetType

def assertNetsHaveConsistentPortNetTypes(obj):
    net_list=obj.getTopology().getNetList()

    for net in net_list:
        # For all nets in component topology, ensure consistent port net type
        net_type=None
        for port_id in net.getPortIdList():
            # For all ports connected by net
            port=obj.getPortById(port_id)
            if net_type is None:
                net_type=port.getNetType().getValue()
            else:
                if port.getNetType().getValue() != net_type:
                    # Assertion should fail if nets types don't match
                    return False
    return True


def predicateIsComponent(obj):
    return type(obj).__name__ == 'Component'

def predicateIsComponentHasNets(obj):
    return predicateIsComponent(obj) and len(obj.getTopology().getNetList())>0
    
#  -- AssertNetHasConsistentPortFormatType: all ports connected by a Net should have a consistent FormatType
#  --- Reuse predicateIsComponentHasNets() from NetHasConsistentPortNetType

def assertNetsHaveConsistentPortFormatTypes(obj):
    net_list=obj.getTopology().getNetList()

    for net in net_list:
        # For all nets in component topology, ensure consistent port net type
        format_type=None
        for port_id in net.getPortIdList():
            # For all ports connected by net
            port=obj.getPortById(port_id)
            if format_type is None:
                format_type=port.getFormatType().getValue()
                print(format_type)
            else:
                if not  FormatType.compareFormatTypes(port.getFormatType(),format_type):                
                    # Assertion should fail if format types don't match                
                    return False

    return True

# - Topology completion rules

# -- CheckComponentHasNoTopologicalHoles: the component should contain no topological holes

def checkComponentHasNoTopologicalHoles(obj):
    return not obj.getTopology().isHole()

# -- CheckComponentHasNoUnknownInterfaceTypes: the component's interface ports should all have known types
#  --- Reuse predicateIsComponent() helper function from NetHasConsistentPortNetType as a predicate

def predicateIsComponentOrSubclass(obj):
    return predicateIsComponent(obj) or type(obj).__name__ == 'Primitive'

def checkComponentHasNoUnknownInterfaceTypes(component):
    
    for port in component.getInterface():
        # Fail check if any interface port has an unknown format type
        if port.getFormatType().isUnknown():
            return False

    return True

# -- CheckComponentHasNoUnknownAttributeTypes: the component's attributes should all have known types

def checkComponentHasNoUnknownAttributeTypes(component):
    
    for att in component.getAttributes():
        # Fail check if any attributes is a FormatType with unknown format type
        if type(att).__name__ == 'FormatType' and att.isUnknown():
            return False

    return True