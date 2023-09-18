from util.helper import info, warn, error
from solver.build import get_buffer_hierarchy
import util.sparseloop_config_processor as sl_config
from util.taxonomy.designelement import Architecture

import solver.model.build_support.abstraction as ab, \
       solver.model.build_support.scale as sc, \
       solver.model.build_support.relations as rn

def build1_graph_representation(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
           buffer_kept_dataspace_by_buffer,buff_dags,constraints=[]):
    info("- build phase 1: graph representation")

    flat_arch=sl_config.flatten_arch_wrapper(arch)

    buffer_hierarchy=get_buffer_hierarchy(arch)

    # Compute flattened port indices
    flat_port_idx_to_dtype={}
    for buffer in buffer_hierarchy:
        flat_port_idx_to_dtype[buffer]=[]
        for dtype in dtype_list:
            flat_port_idx_to_dtype[buffer].extend([dtype]*len(fmt_iface_bindings[buffer][dtype]))

    taxo_uarch=Architecture.fromDict(sl_config.load_config_yaml('ref_output/new_arch.yaml'))

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

    reln_list=rn.get_scale_boundary_conditions(gpthrpt,port_attr_dict,fmt_iface_bindings, \
                                               flat_arch,buff_dags,dtype_list,constraints=constraints)

    info("- => Done, build phase 1.")

    return {'reln_list':reln_list,'port_list':port_list,'port_attr_dict':port_attr_dict,'net_list':net_list, \
            'out_port_net_dict':out_port_net_dict,'in_port_net_dict':in_port_net_dict,'symbol_list':symbol_list,'uarch_symbol_list':uarch_symbol_list, \
            'obj_to_ports':obj_to_ports,'gpthrpt':gpthrpt,'obj_dict':obj_dict}