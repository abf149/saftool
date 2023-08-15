'''Useful transformations against design elements'''

def transformFloodNetFormatToObjPorts(obj):
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

def transformFloodNetFormatToChildPorts(obj):
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