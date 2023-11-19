from util.helper import info, warn, error
from solver.build import get_buffer_hierarchy
import util.notation.predicates as p_
import solver.model.build_support.abstraction as ab_
import util.sparseloop_config_processor as sl_config
from util.taxonomy.designelement import Architecture

import solver.model.build_support.abstraction as ab, \
       solver.model.build_support.scale as sc, \
       solver.model.build_support.relations as rn

# This function takes an architecture object and returns a dictionary mapping uarch ports to buffer ports
def get_uarch_port_mapping_to_buffer_port(obj):

    # Initialize an empty dictionary to store the mapping
    mapping = {}
    # Check if the object is an architecture
    if p_.isArchitecture(obj):
        # Get the list of subcomponents of the architecture
        components = obj.getTopology().getComponentList()
        pref=obj.getId()
        # Loop through each subcomponent
        for component in components:
            # Check if the subcomponent is a buffer stub
            if p_.isCategory(component,"BufferStub"):
                # Get the uri of the buffer stub
                buffer_id=component.getId()
                buffer_uri = ab_.uri(pref,buffer_id)
                # Get the list of ports of the buffer stub
                buffer_ports = component.getInterface()
                # Loop through each port of the buffer stub
                for buffer_port in buffer_ports:
                    # Get the uri of the buffer port
                    buffer_port_uri = ab_.uri(buffer_uri,buffer_port.getId())
                    # Get the list of nets connected to the buffer port
                    buffer_nets = obj.getTopology().getNetList()
                    # Loop through each net connected to the buffer port
                    for buffer_net in buffer_nets:
                        # Get the list of ports connected by the net
                        net_ports = buffer_net.getPortIdList()

                        relevant_net=False
                        buffer_port_id=buffer_port.getId()
                        for net_port in net_ports:
                            #print(net_port,buffer_port.getId())
                            if net_port==ab_.uri(buffer_id,buffer_port_id):
                                relevant_net=True

                        if relevant_net:
                            # Loop through each port connected by the net
                            for net_port in net_ports:
                                net_port_uri=ab_.uri(pref,net_port)

                                # Check if the port is not the same as the buffer port
                                if net_port_uri != buffer_port_uri and "." in net_port:
                                    net_port_comp_id=net_port.split(".")[0]
                                    # Get the uri of the port
                                    #net_port_uri = net_port.getUri()
                                    # Get the parent component of the port
                                    net_component = [c_ for c_ in components if c_.getId()==net_port_comp_id][0]
                                    # Check if the parent component is a uarch
                                    if not p_.isPrimitive(net_component):
                                        # Get the uri of the uarch
                                        uarch_uri = ab_.uri(pref,net_component.getId())
                                        # Check if the uarch uri is already in the mapping
                                        mapping.setdefault(uarch_uri,{}).setdefault(net_port,[]).append((buffer_uri, buffer_port_uri))

    # Return the mapping dictionary
    return mapping

def build1_graph_representation(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                buffer_kept_dataspace_by_buffer,buff_dags,constraints=[]):
    warn("- Build phase 1: graph representation")

    flat_arch=sl_config.flatten_arch_wrapper(arch)

    buffer_hierarchy=get_buffer_hierarchy(arch)

    # Compute flattened port indices
    flat_port_idx_to_dtype={}
    for buffer in buffer_hierarchy:
        flat_port_idx_to_dtype[buffer]=[]
        for dtype in dtype_list:
            flat_port_idx_to_dtype[buffer].extend([dtype]*len(fmt_iface_bindings[buffer][dtype]))

    port_list, \
    port_attr_dict, \
    net_list, \
    out_port_net_dict, \
    in_port_net_dict, \
    symbol_list, \
    uarch_symbol_list, \
    obj_to_ports=ab.get_port_uris_and_attributes_and_nets_wrapper(taxo_uarch,flat_arch)

    obj_dict={}
    ab.build_component_dict(taxo_uarch,obj_dict)

    gpthrpt= \
        sc.get_global_positional_throughput(flat_arch,buffer_hierarchy,buffer_kept_dataspace_by_buffer, \
                                            buff_dags,dtype_list)

    llbs={dtype:[buff for idx,buff in enumerate(flat_arch) if buff_dags[dtype][idx][-1]] for dtype in dtype_list}
    reln_list=rn.get_scale_boundary_conditions(gpthrpt,port_attr_dict,fmt_iface_bindings, \
                                               flat_arch,buff_dags,dtype_list,constraints=constraints)

    uarch_port_upstream_map=get_uarch_port_mapping_to_buffer_port(taxo_uarch)

    warn("- => done, build phase 1.")

    return {'reln_list':reln_list,'port_list':port_list,'port_attr_dict':port_attr_dict,'net_list':net_list, \
            'out_port_net_dict':out_port_net_dict,'in_port_net_dict':in_port_net_dict,'symbol_list':symbol_list,'uarch_symbol_list':uarch_symbol_list, \
            'obj_to_ports':obj_to_ports,'gpthrpt':gpthrpt,'obj_dict':obj_dict,'uarch_port_upstream_map':uarch_port_upstream_map, \
            'buff_dags':buff_dags,'llbs':llbs}