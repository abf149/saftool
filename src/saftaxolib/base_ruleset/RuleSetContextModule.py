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

def predicateIsArchitecture(obj):
    return type(obj).__name__ == 'Architecture'

def predicateIsComponentOrArchitectureHasNets(obj):
    return (predicateIsComponent(obj) or predicateIsArchitecture(obj)) and len(obj.getTopology().getNetList())>0
    
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
            else:
                if not  FormatType.compareFormatTypes(port.getFormatType(),format_type):                
                    # Assertion should fail if format types don't match                
                    return False

    return True

# - Topology rewrite rules

# -- TransformUnknownPortTypesOnNetsWithKnownTypesToKnownType: infer unknown port types on nets where some port types are known

def transformUnknownPortTypesOnNetsWithKnownTypesToKnownType(obj):
    net_list=obj.getTopology().getNetList()
    iface=obj.getInterface() # TODO: hack for not having a good port read/modify/write

    for port in iface:
        # Look for unknown port types on nets with known port types. 
        if port.getFormatType().isUnknown():
            # For each port of unknown type in the component interface,
            for net in net_list:
                if port.getId() in net.getPortIdList():
                    # find any connected net(s) and attempt to infer net type from a connected port of known type.
                    net_type_str=None
                    for connected_port_id in net.getPortIdList():
                        if not obj.getPortById(connected_port_id).getFormatType().isUnknown():
                            net_type_str=obj.getPortById(connected_port_id).getFormatType().getValue()
                            break
                    if net_type_str is not None:
                        # Upon successful net-type inference, update the unknown port type to a known value.
                        new_format_type=port.getFormatType()
                        new_format_type.setValue(net_type_str)
                        port.setFormatType(new_format_type)
                    

    obj.setInterface(iface)
    return obj

def predicateIsComponentOrArchitectureAndHasNetsHasUnknownPortTypesOnNetsWithKnownTypes(obj):
    #if not ((predicateIsComponent(obj) or type(obj).__name__ == 'Primitive') and len(obj.getTopology().getNetList())>0):
    if not (predicateIsComponentOrArchitectureHasNets(obj)):
        return False

    net_list=obj.getTopology().getNetList()

    for port in obj.getInterface():
        # Look for unknown port types on nets with known port types. 
        if port.getFormatType().isUnknown():
            # For each port of unknown type in the component interface,
            for net in net_list:
                if port.getId() in net.getPortIdList():
                    # examine all component topology nets connected to the port of unknown type,
                    for connected_port_id in net.getPortIdList():
                        if not obj.getPortById(connected_port_id).getFormatType().isUnknown():
                            # and return True if the net's type can be inferred from connected ports of known type.
                            return True

    return False

# -- TransformUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType: infer unknown child component port types on nets where some port types are known

def transformUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType(obj):
    net_list=obj.getTopology().getNetList()
    comp_list=obj.getTopology().getComponentList() # TODO: hack for not having a good component read/modify/write     

    for subcomponent in comp_list:
        # Examine all subcomponents.
        subcomponent_id=subcomponent.getId() 
        iface=subcomponent.getInterface() # TODO: hack for not having a good port read/modify/write       
        for port in iface:
            # Look for unknown port types on nets with known port types. 
            if port.getFormatType().isUnknown():
                # For each port of unknown type in the subcomponent interface,
                full_port_id=subcomponent_id+'.'+port.getId()
                for net in net_list:
                    if full_port_id in net.getPortIdList():
                        # find any connected net(s) and attempt to infer net type from a connected port of known type.
                        net_type_str=None
                        for connected_port_id in net.getPortIdList():
                            if not obj.getPortById(connected_port_id).getFormatType().isUnknown():
                                net_type_str=obj.getPortById(connected_port_id).getFormatType().getValue()
                                break
                        if net_type_str is not None:
                            # Upon successful net-type inference, update the unknown port type to a known value.
                            new_format_type=port.getFormatType()
                            new_format_type.setValue(net_type_str)
                            port.setFormatType(new_format_type)

        subcomponent.setInterface(iface)
    
    topology=obj.getTopology()
    topology.setComponentList(comp_list)
    obj.setTopology(topology)
    return obj

def predicateIsComponentHasNetsHasUnknownChildComponentPortTypesOnNetsWithKnownTypes(obj):
    #if not ((predicateIsComponent(obj) or type(obj).__name__ == 'Primitive') and len(obj.getTopology().getNetList())>0):
    if not (predicateIsComponentOrArchitectureHasNets(obj)):
        return False

    net_list=obj.getTopology().getNetList()

    for subcomponent in obj.getTopology().getComponentList():
        # Examine all subcomponents.
        subcomponent_id=subcomponent.getId()
        for port in subcomponent.getInterface():    
            if port.getFormatType().isUnknown():
                # For each port of unknown type in the subcomponent interface,
                full_port_id=subcomponent_id+'.'+port.getId()
                for net in net_list:
                    if full_port_id in net.getPortIdList():
                        # examine all component topology nets connected to the port of unknown type,
                        for connected_port_id in net.getPortIdList():
                            if not obj.getPortById(connected_port_id).getFormatType().isUnknown():
                                # and return True if the net's type can be inferred from connected ports of known type.
                                print("TransformUnknownChildComponentPortTypesOnNetsWithKnownTypesToKnownType rewrite:")
                                print("- Component:", obj.getId())
                                print("- Port with known net type:",connected_port_id)
                                print("- Net type:",obj.getPortById(connected_port_id).getFormatType().getValue())
                                print("- Port with unknown net type:",full_port_id)
                                return True

    return False

# - Topology completion rules

# -- CheckComponentHasNoTopologicalHoles: the component should contain no topological holes

def checkComponentHasNoTopologicalHoles(obj):
    return not obj.getTopology().isHole()

# -- CheckComponentHasNoUnknownInterfaceTypes: the component's interface ports should all have known types
#  --- Reuse predicateIsComponent() helper function from NetHasConsistentPortNetType as a predicate

def predicateIsComponentOrPrimitive(obj):
    return predicateIsComponent(obj) or type(obj).__name__ == 'Primitive'

def checkComponentHasNoUnknownInterfaceTypes(component):
    for port in component.getInterface():
        # Fail check if any interface port has an unknown format type
        if port.getFormatType().isUnknown():
            print('\nFailed',checkComponentHasNoUnknownInterfaceTypes,'details:')
            print('- Component id:',component.getId())
            print('- Port id:',port.getId())
            print('- Port format:',port.getFormatType())
            return False

    return True

# -- CheckComponentHasNoUnknownAttributeTypes: the component's attributes should all have known types

def checkComponentHasNoUnknownAttributeTypes(component):
    
    for att in component.getAttributes():
        # Fail check if any attributes is a FormatType with unknown format type
        if type(att).__name__ == 'FormatType' and att.isUnknown():
            return False

    return True