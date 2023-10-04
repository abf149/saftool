'''Solver phase 1: DFS'''
from util.helper import info, warn, error
import solver.model.build_support.relations as rn
import solver.model.build_support.scale as sc
import saflib.microarchitecture.model.ModelRegistry as mr
import solver.model.build_support.abstraction as ab_

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
    info("-- Applying transitive closure to discover relations between primitive ports.")
    transitive_closure_relns={"eq":[],"ineq":[]}
    port_visited=[False]*len(port_list)

    for root_port in port_list:
        transitive_dfs_from_primitive_port(root_port,root_port,port_list,net_list,out_port_net_dict,port_attr_dict, \
                                           port_visited,transitive_closure_relns,reln_dict)

    info("-- => Done, transitive closure")
    return transitive_closure_relns

def significant_fmt_iface_idxs(fmt_uarch_uri,uarch_port_upstream_map,fmt_iface_bindings,dtype_list,llbs):
    '''
    Identify the format interface indices which are significant for modeling.\n\n

    Arguments:\n
    - uarch_port_upstream_map -- dict[component uri] = {port uri:[(buffer uri,port uri),...], port uri:...}\n
    - fmt_iface_bindings -- metadata format bindings to buffer format ifaces, formatted as\n\n

      dict[buffer][datatype] -> [format_type,format_type]\n
    - dtype_list -- list of datatypes
    '''
    port_upstreams=uarch_port_upstream_map[fmt_uarch_uri]
    buffer_uri=port_upstreams[list(port_upstreams.keys())[0]][0][0]
    buffer_id=buffer_uri.split(".")[-1]
    significant_idxs=[]
    idx=0
    for dtype in dtype_list:
        if buffer_id in llbs[dtype]:
            llb_dtype_last_fmt_iface_idx=len(fmt_iface_bindings[buffer_id][dtype])-1
            for rdx,_ in enumerate(fmt_iface_bindings[buffer_id][dtype]):
                if rdx==llb_dtype_last_fmt_iface_idx:
                    significant_idxs.append(idx)
                idx+=1
        else:
            for _,_ in enumerate(fmt_iface_bindings[buffer_id][dtype]):
                idx+=1            

    return significant_idxs

def component_relations(obj_dict,user_attributes,fmt_iface_bindings,dtype_list, \
                        llbs,uarch_port_upstream_map):
    '''
    Assemble the key relations needed to apply scale inference to components.\n\n

    Arguments:\n
    - obj_dict -- a dictionary of design object -> properties dict\n
    - user_attributes -- a dictionary of user-specified attributes such as clock_period,
                         technology, etc.\n
    - fmt_iface_bindings -- metadata format bindings to buffer format ifaces, formatted as\n\n

      dict[buffer][datatype] -> [format_type,format_type]\n
    - dtype_list -- list of datatypes\n
    - llbs -- dict[datatype] = list of last level buffers (should be length <= 1)\n\n

    Returns:\n
    - symbols -- List of symbols (as strings) over all primitive relations\n
    - symbol_types -- Symbol types\n
    - constraints -- relations, as strings, representing equations and inequalities\n
    - energy_objective_graphs -- dictionary of energy objective graphs, by component\n
    - area_objective_graphs -- dictionary of area objective graphs, by component\n
    - yields -- dictionary; keys are a subset of symbols required for building models later\n
    - primitive_models -- dictionary of component model structures
    '''
    info("-- Building primitive scale inference problems.")

    clock_period=user_attributes['clock_period']
    technology=user_attributes['technology']

    symbols=[]
    symbol_types=[]
    constraints=[]
    energy_objectives={}
    area_objectives={}
    yields={}
    component_models={}
    sub_action_graph={}

    for comp_name in obj_dict:
        dct=obj_dict[comp_name]
        if dct["microarchitecture"] and (not dct["primitive"]):
            # Considering non-primitive components only

            comp=obj_dict[comp_name]["obj"]
            uri_prefix=obj_dict[comp_name]["uri_prefix"]
            modelBase=mr.getComponent(comp.getCategory()+"Model")
            info("--- Building",comp_name,"primitive scale inference problem.")            
            compModel=modelBase.copy() \
                               .set_scale_parameter("clock",clock_period,param_type="real") \
                               .set_scale_parameter("technology",technology,param_type="string")
            
            if "FormatUarch" in comp.getCategory():
                idxs=significant_fmt_iface_idxs(comp_name, \
                                            uarch_port_upstream_map, \
                                            fmt_iface_bindings, \
                                            dtype_list, \
                                            llbs)
                warn("---- Detected format microarchitecture (FormatUarch)" + \
                     "with significant fmt ifaces",idxs)
                compModel=compModel.set_scale_parameter("high_impact_mdparser_indices", \
                                                        significant_fmt_iface_idxs(comp_name, \
                                                                                   uarch_port_upstream_map, \
                                                                                   fmt_iface_bindings, \
                                                                                   dtype_list, \
                                                                                   llbs), \
                                                        param_type="list")

            compModel=compModel.from_taxo_obj(comp) \
                               .set_uri_prefix(uri_prefix) \
                               .build_symbols_constraints_objectives_attributes()

            component_models[comp_name]=compModel

            # Get primitive characteristic relations
            comp_symbols, \
            comp_symbol_types, \
            comp_constraints, \
            comp_energy_objectives, \
            comp_area_objectives, \
            comp_yields = compModel.get_scale_inference_problem()

            comp_sub_action_graph = \
                compModel.get_subaction_graph()

            symbols.extend(comp_symbols)
            symbol_types.extend(comp_symbol_types)
            constraints.extend(comp_constraints)
            energy_objectives[comp_name]=comp_energy_objectives
            area_objectives[comp_name]=comp_area_objectives
            yields[comp_name]=comp_yields
            sub_action_graph[comp_name]=comp_sub_action_graph
            info("--- Done,",comp_name)

    info("-- => Done, component scale inference problems.")
    return symbols,symbol_types,constraints,energy_objectives, \
           area_objectives,yields,component_models, sub_action_graph

def primitive_relations(obj_dict,user_attributes):
    '''
    Assemble the key relations needed to apply scale inference to primitives.\n\n

    Arguments:\n
    - obj_dict -- a dictionary of design object -> properties dict\n
    - user_attributes -- a dictionary of user-specified attributes such as clock_period,
                         technology, etc.\n\n

    Returns:\n
    - symbols -- List of symbols (as strings) over all primitive relations\n
    - symbol_types -- Symbol types\n
    - constraints -- relations, as strings, representing equations and inequalities\n
    - energy_objectives -- dictionary of energy objectives, by component\n
    - area_objectives -- dictionary of area objectives, by component\n
    - yields -- dictionary; keys are a subset of symbols required for building models later\n
    - primitive_models -- dictionary of component model structures
    '''
    info("-- Building primitive scale inference problems.")

    clock_period=user_attributes['clock_period']
    technology=user_attributes['technology']

    symbols=[]
    symbol_types=[]
    constraints=[]
    energy_objectives={}
    area_objectives={}
    yields={}
    primitive_models={}

    for comp_name in obj_dict:
        dct=obj_dict[comp_name]
        if dct["microarchitecture"] and dct["primitive"]:
            # Considering microarchitectural primitives only

            comp=obj_dict[comp_name]["obj"]
            uri_prefix=obj_dict[comp_name]["uri_prefix"]
            modelBase=mr.getPrimitive(comp.getCategory()+"Model")
            info("--- Building",comp_name,"primitive scale inference problem.")
            compModel=modelBase.copy() \
                               .set_scale_parameter("clock",clock_period,param_type="real") \
                               .set_scale_parameter("technology",technology,param_type="string") \
                               .from_taxo_obj(comp) \
                               .set_uri_prefix(uri_prefix) \
                               .build_symbols_constraints_objectives_attributes()

            primitive_models[comp_name]=compModel

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

            info("--- Done,",comp_name)

    info("-- => Done, primitive scale inference problems.")
    return symbols,symbol_types,constraints,energy_objectives, \
           area_objectives,yields,primitive_models

def build_component_energy_objective(component_uri,implementation_id,sub_action_graph,energy_objectives,
                                     include_spec=None,exclude_spec=None):
    '''
    Build component energy objective function.\n\n

    The energy objective function for a component is the sum of the energy-
    per-action for all of the component's actions.\n\n

    Each action's energy is the sum of the energies of all of its associated
    sub-component sub-actions, i.e. component action x triggers sub-action y against
    sub-component A and sub-action z against sub-component B; then the total action
    energy is the energy of sub-action y plus the energy of sub-action z.

    Arguments:\n
    - component_uri -- component uri (string)
    - implementation_id -- implementation id (string)\n
    - sub_action_graph -- graph representation of how component action energies are constructed
                          from primitive action energies.\n\n

      dict[component uri] = [{'impl_': implementation string id,
                              'action_name_': string,
                              'sub_component': string (optionally with variable i.e. $x),
                              'sub_action': string,
                              'arg_map': {action arg name string:sub_action arg name string}},
                              {...},
                              ...]\n\n
    
    - energy_objectives -- dict[primitive uri] = {action name: string expression, ...}\n
    - include_spec -- list of string uris of components to include 
                      in the global energy objective. If None, include all.\n
    - exclude_spec -- list of string uris of components to exclude
                      from the global energy objective. If None, exclude None.
    '''

    if (include_spec is not None) and (component_uri not in include_spec):
        # No energy contribution if there is an include spec and this
        # component is not in it
        return None
    
    if (exclude_spec is not None) and (component_uri in exclude_spec):
        # No energy contribution is there is an exclude spec and this
        # component is in it
        return None

    # 1. Get subgraph application to component implementation
    action_energy_dict={}
    comp_impl_sub_action_graph=[edge for edge in sub_action_graph[component_uri] \
                                    if edge['impl_']==implementation_id]
    
    # 2. Group sub-action energy expression by the parent action
    action_energy_objectives={}
    for edge in comp_impl_sub_action_graph:
        subcomp_uri=ab_.uri(component_uri,edge['sub_component'])

        if ((include_spec is None) or (subcomp_uri in include_spec)) and \
                ((exclude_spec is None) or (subcomp_uri not in exclude_spec)):
            # Only include sub-action energy for subcomponents permitted by
            # the include/exclude specs
            action_energy_objectives.setdefault(edge['action_name_'],[]) \
                .append(energy_objectives[subcomp_uri][edge['sub_action']])

    # 3. Build action energy expressions
    action_energy_expressions={}
    for action in action_energy_objectives:
        expr=action_energy_expressions.setdefault(action,"")
        for sub_expr in action_energy_objectives[action]:
            expr=expr+" + "+sub_expr

    # 4. Build expression for component energy objective from weighted sum of action energies
    #if action_weights_dict is None:
    #    num_actions=len(list(action_energy_expressions.keys()))
    #    action_weights_dict = \
    #        {action:(1/num_actions) for action in action_energy_expressions}
    #component_energy_objective=""
    #for action in action_energy_expressions:
    #    component_energy_objective = \
    #        component_energy_objective + " + " + str(action_weights_dict[action]) + \
    #        "* (" + action_energy_expressions[action] + ")"

    return action_energy_expressions

def build_component_area_objective(component_uri,implementation_id,subcomponent_id_list, \
                                   area_objectives,include_spec=None,exclude_spec=None):
    '''
    Build component area objective function.\n\n

    The area objective function for a component is the sum of the area
     for all of the subcomponents.\n\n

    Arguments:\n
    - component_uri -- component uri (string)
    - implementation_id -- implementation id (string)\n
    - area_objectives -- dict[component uri] = string expression\n
    - include_spec -- list of string uris of components to include 
                      in the global energy objective. If None, include all.\n
    - exclude_spec -- list of string uris of components to exclude
                      from the global energy objective. If None, exclude None.
    '''

    if (include_spec is not None) and (component_uri not in include_spec):
        # No energy contribution if there is an include spec and this
        # component is not in it
        return None
    
    if (exclude_spec is not None) and (component_uri in exclude_spec):
        # No energy contribution is there is an exclude spec and this
        # component is in it
        return None

    # Build action energy expressions
    area_expression=""
    for subcomponent_id in subcomponent_id_list:
        subcomp_uri=ab_.uri(component_uri,subcomponent_id)
        if ((include_spec is None) or (subcomp_uri in include_spec)) and \
                ((exclude_spec is None) or (subcomp_uri not in exclude_spec)):
            # Only include sub-component area for subcomponents permitted by
            # the include/exclude specs
            area_expression = area_expression + " + " + area_objectives[subcomp_uri]

    return area_expression

def build_global_energy_objective(primitive_models,component_models,energy_objectives, \
                                  sub_action_graph, include_spec=None,exclude_spec=None):
    '''
    Build global energy objective functions.\n\n

    The global energy objective is the sum 

    Arguments:\n
    - primitive_models --
    - component_models --
    - energy_objectives -- dict[component uri] = {action name: string expression, ...}\n
    - sub_action_graph -- graph representation of how component action energies are constructed
                          from primitive action energies.\n\n

      dict[component uri] = [{'impl_': implementation string id,
                              'action_name_': string,
                              'sub_component': string (optionally with variable i.e. $x),
                              'sub_action': string,
                              'arg_map': {action arg name string:sub_action arg name string}},
                              {...},
                              ...]\n\n
    
    - include_spec -- list of string uris of components to include 
                      in the global energy objective. If None, include all.\n
    - exclude_spec -- list of string uris of components to exclude
                      from the global energy objective. If None, exclude None.
    '''

    global_energy_objective=""


def build_global_area_objective(area_objectives,include_spec=None,exclude_spec=None):
    '''
    Build global area objective functions.\n\n

    The globnal 

    Arguments:\n
    - area_objectives -- dict[component uri] = {action name: string expression, ...}\n
    - include_spec -- list of string uris of components to include 
                      in the global energy objective. If None, include all.\n
    - exclude_spec -- list of string uris of components to exclude
                      from the global energy objective. If None, exclude None.
    '''
    global_area_objective=""

def build_global_objectives(energy_objectives,area_objectives,sub_action_graph, \
                            include_spec=None,exclude_spec=None):
    '''
    Build global energy/area objective functions.\n\n

    Arguments:\n
    - energy_objectives -- \n
    - area_objectives -- \n
    - sub_action_graph -- graph representation of how component action energies are constructed
                          from primitive action energies
    '''
    global_energy_objective=""
    global_area_objective=""
    return global_energy_objective, global_area_objective

def build2_system_of_relations(sclp,user_attributes,fmt_iface_bindings,dtype_list):
    '''
    Express the scale inference problem as a system of relations which constrain the individual
    port scale parameters as well as the data throughput at each port.\n\n

    Arguments:\n
    - sclp -- scale problem description (as graph). Required dict fields:\n\n

      sclp['reln_list'] - dict[port uri] = [eqn_or_ineq_as_str,eqn_or_ineq_as_str,...]\n
      sclp['port_list] - list of port uris
      sclp['port_attr_dict'] - dict[port uri] = {'obj': component uri, 'ww':int, 'pw':int, 'microarchitecture':bool,\n
                                                 'primitive':bool}
      sclp['net_list'] - list of {'net_uri':net uri,'out_port':port uri, 'in_ports':list of port uris}
      sclp['out_port_net_dict'] - dict[port uri] = index into net_list
      sclp['obj_dict'] - dict[component uri] = {'obj':primitive design element, 'microarchitecture':bool,
                                                'primitive':bool,'uri_prefix':str}
      sclp['uarch_port_upstream_map'] - dict[component uri] = {port uri:[(buffer uri,port uri),...], port uri:...}
      sclp['llbs'] - dict[datatype] = list of last level buffers (should be length <= 1)

    - user_attributes -- user-specified solver attributes\n
    - fmt_iface_bindings -- metadata format bindings to buffer format ifaces, formatted as\n\n

      dict[buffer][datatype] -> [format_type,format_type]\n
    - dtype_list -- list of datatypes
    '''
    warn("- Build phase 2: system of relations")

    rlns=sclp['reln_list']
    port_list=sclp['port_list']
    port_attr_dict=sclp['port_attr_dict']
    net_list=sclp['net_list']
    out_port_net_dict=sclp['out_port_net_dict']
    obj_dict=sclp['obj_dict']
    uarch_port_upstream_map=sclp['uarch_port_upstream_map']
    llbs=sclp['llbs']

    # Get system of relations describing supported primitive configurations
    primitive_symbols, \
    primitive_symbol_types, \
    primitive_constraints, \
    primitive_energy_objectives, \
    primitive_area_objectives, \
    primitive_yields, \
    primitive_models = primitive_relations(obj_dict,user_attributes)

    component_symbols, \
    component_symbol_types, \
    component_constraints, \
    component_energy_objectives, \
    component_area_objectives, \
    component_yields, \
    component_models, \
    sub_action_graph = \
        component_relations(obj_dict,user_attributes, \
                            fmt_iface_bindings, \
                            dtype_list, \
                            llbs, \
                            uarch_port_upstream_map)

    # Get additional relations which express connections between primitives
    transitive_relations = \
           transitive_closure_dfs(port_list,net_list,out_port_net_dict,port_attr_dict,rlns) 

    symbols=primitive_symbols+component_symbols
    symbol_types=primitive_symbol_types+component_symbol_types
    constraints=primitive_constraints+component_constraints
    constraints.extend(transitive_relations['eq'])
    constraints.extend(transitive_relations['ineq'])
    energy_objectives={}
    energy_objectives.update(primitive_energy_objectives )
    energy_objectives.update(component_energy_objectives)
    area_objectives={}
    area_objectives.update(primitive_area_objectives)
    area_objectives.update(component_area_objectives)
    yields={}
    yields.update(primitive_yields)
    yields.update(component_yields)
    models={}
    models.update(primitive_models)
    models.update(component_models)

    print(area_objectives)

    assert(False)

    global_energy_objective, global_area_objective = \
        build_global_objectives(energy_objectives,area_objectives,sub_action_graph)

    warn("- => done, build phase 2.")

    return {"symbols":symbols, "symbol_types":symbol_types, "constraints":constraints, \
            "energy_objectives":energy_objectives, "area_objectives":area_objectives, \
            "yields":yields, "primitive_models":primitive_models, "component_models":component_models, \
            "sub_action_graph":sub_action_graph, "global_energy_objective":global_energy_objective, \
            "global_area_objective":global_area_objective}