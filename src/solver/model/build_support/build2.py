'''Solver phase 1: DFS'''
from util.helper import info, warn, error
import solver.model.build_support.relations as rn
import solver.model.build_support.scale as sc
import saflib.microarchitecture.model.ModelRegistry as mr

def subs_scale_param_boundary_conds(port_with_boundary_conds,subs_port,reln_dict,transitive_closure_relns):
    for partial_reln in reln_dict[port_with_boundary_conds]:
        transitive_closure_relns['ineq'].append(subs_port+"_"+partial_reln)

def add_scale_param_eqns(root_port,dst_port,transitive_closure_relns):
    for attr_suffix in sc.sym_suffixes:
        transitive_closure_relns['eq'].append(root_port+"_"+attr_suffix + \
                                        " == " + \
                                        dst_port+"_"+attr_suffix)

def transitive_dfs_from_primitive_port(root_port,src_port,port_list,net_list,port_net_dict,port_attr_dict, \
                                       port_visited,transitive_closure_relns,reln_dict):
    root_is_buffer_stub_port=not port_attr_dict[root_port]['microarchitecture']
    root_is_primitive_port=port_attr_dict[root_port]['primitive']    
    src_port_idx=port_list.index(src_port)
    if port_visited[src_port_idx] or ((not root_is_buffer_stub_port) and (not root_is_primitive_port)):
        # Port in-degree <= 1 and root port must belong to a primitive or a buffer stub
        return
    else:
        assert(root_is_buffer_stub_port or root_is_primitive_port)
        port_visited[src_port_idx]=True

    src_is_buffer_stub_port=not port_attr_dict[src_port]['microarchitecture']
    src_is_primitive_port=port_attr_dict[src_port]['primitive']
    if root_port != src_port:
        # Establish relationship between root port and downstream ports of interest
        if root_is_buffer_stub_port and src_is_primitive_port:
            # Substitute this primitive port into root buffer-stub port inequalities
            subs_scale_param_boundary_conds(root_port,src_port,reln_dict,transitive_closure_relns)
        elif root_is_primitive_port and src_is_buffer_stub_port:
            # Substitute root primitive port into this buffer-stub port's inequalities
            subs_scale_param_boundary_conds(src_port,root_port,reln_dict,transitive_closure_relns)
        elif root_is_primitive_port and src_is_primitive_port:
            # Establish equality between this primitive port and root primitive port
            add_scale_param_eqns(root_port,src_port,transitive_closure_relns)

    dst_ports=[]
    if src_port in port_net_dict:
        #assert((not src_is_primitive_port) or len(net_list[port_net_dict[src_port]]['in_ports'])==0)
        dst_ports=net_list[port_net_dict[src_port]]['in_ports']

    #for dst_port in dst_ports:
    #    # New relations: src_ports' scale params are transitive to dst_ports
    #    add_scale_param_eqns(src_port,dst_port,transitive_closure_relns)
    for dst_port in dst_ports:
        #DFS
        transitive_dfs_from_primitive_port(root_port,dst_port,port_list,net_list,port_net_dict,port_attr_dict, \
                                           port_visited,transitive_closure_relns,reln_dict)

def transitive_closure_dfs(port_list,net_list,out_port_net_dict,port_attr_dict,reln_dict):
    '''
    DFS algorithm to infer microarchitecture port scale parameters based on boundary conditions at
    architecture buffer ports
    '''
    transitive_closure_relns={"eq":[],"ineq":[]}
    port_visited=[False]*len(port_list)

    for root_port in port_list:
        transitive_dfs_from_primitive_port(root_port,root_port,port_list,net_list,out_port_net_dict,port_attr_dict, \
                                           port_visited,transitive_closure_relns,reln_dict)

    return transitive_closure_relns

def primitive_relations(obj_dict):
    '''
    Assemble the key relations needed to apply scale inference to primitives
    '''

    symbols=[]
    symbol_types=[]
    constraints=[]
    energy_objectives={}
    area_objectives={}
    yields={}

    for comp_name in obj_dict:
        dct=obj_dict[comp_name]
        if dct["microarchitecture"] and dct["primitive"]:
            comp=obj_dict[comp_name]["obj"]
            uri_prefix=obj_dict[comp_name]["uri_prefix"]
            modelBase=mr.getModel(comp.getCategory()+"Model")
            compModel=modelBase.copy() \
                               .from_taxo_obj(comp) \
                               .build_symbols_constraints_objectives_attributes(uri_prefix)

            # Get primitive characteristic relations
            comp_symbols, \
            comp_symbol_types, \
            comp_constraints, \
            comp_energy_objectives, \
            comp_area_objectives, \
            comp_yields = compModel.get_scale_inference_problem()

            symbols.extend(comp_symbols)
            symbol_types.extend(comp_symbol_types)
            constraints.extend(comp_constraints)
            energy_objectives[comp_name]=comp_energy_objectives
            area_objectives[comp_name]=comp_area_objectives
            yields[comp_name]=comp_yields

    return symbols,symbol_types,constraints,energy_objectives,area_objectives,yields

def build2_system_of_relations(sclp):
    info("- build phase 2: system of relations")

    rlns=sclp['reln_list']
    port_list=sclp['port_list']
    port_attr_dict=sclp['port_attr_dict']
    net_list=sclp['net_list']
    out_port_net_dict=sclp['out_port_net_dict']
    obj_dict=sclp['obj_dict']

    # Get system of relations describing supported primitive configurations
    symbols, \
    symbol_types, \
    constraints, \
    energy_objectives, \
    area_objectives, \
    yields = primitive_relations(obj_dict)

    # Get additional relations which express connections between primitives
    constraints.extend( \
           transitive_closure_dfs(port_list,net_list,out_port_net_dict,port_attr_dict,rlns))  

    info("- => Done, build phase 2.")

    return {"symbols":symbols, "symbol_types":symbol_types, "constraints":constraints, \
            "energy_objectives":energy_objectives, "area_objectives":area_objectives, "yields":yields}