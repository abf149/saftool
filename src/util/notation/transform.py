'''Useful transformations against design elements'''
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *

def net_zip(port_name_expressions,port_net_type_strs,component_names,gen_type='rank_list',gen_attr=[]):
    net_list=[]

    idx=0
    for fiber in gen_attr:
        # Repeat the same pattern of ports for each fiber format
        # $v = fiber format
        # $x = fiber index
        for pn_exps,net_type_str in zip(port_name_expressions,port_net_type_strs):
            full_port_ids=[component_name+'.'+pn_exp.replace("$x",str(idx)).replace("$v",fiber.getValue()) \
                            for component_name,pn_exp in zip(component_names,pn_exps)]

            net_type=NetType.fromIdValue("TestNetType",net_type_str)
            format_type=FormatType.fromIdValue('TestFormatType','?')
            net_name=full_port_ids[0]
            for kdx in range(1,len(full_port_ids)):
                net_name += '_' + full_port_ids[kdx]
            net_list.append(Net.fromIdAttributes(net_name, net_type, format_type, full_port_ids))

        idx+=1   

    return net_list 

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

def transformTopology(obj,new_component_list,new_net_list,append=True):
    arch_topology=obj.getTopology()
    if append:
        arch_topology.setComponentList(arch_topology.getComponentList()+list(new_component_list))
        arch_topology.setNetList(arch_topology.getNetList()+list(new_net_list))
    else:
        arch_topology.setComponentList(list(new_component_list))
        arch_topology.setNetList(list(new_net_list))

    obj.setTopology(arch_topology)    
    return obj

def transformSAFs(obj,new_saf_list,append=True):
    if append:
        obj.setSAFList(obj.getSAFList()+list(new_saf_list))
    else:
        obj.setSAFList(list(new_saf_list))
    return obj

def transformObjAttribute(obj,value,idx):
    obj.setAttributeByIndex(value,idx)
    return obj