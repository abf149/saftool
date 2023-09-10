'''Solver phase 1: DFS'''
import solver.model.build_support.relations as rn
import solver.model.build_support.scale as sc

def add_scale_param_eqns(src_port,dst_port,transitive_closure_relns):
    for attr_suffix in sc.sym_suffixes:
        transitive_closure_relns.append(src_port+"_"+attr_suffix + \
                                        " == " + \
                                        dst_port+"_"+attr_suffix)

def transitive_dfs(src_port,port_list,net_list,port_net_dict, \
                   port_visited,transitive_closure_relns,from_out_port):
    src_port_idx=port_list.index(src_port)
    if port_visited[src_port_idx]:
        return
    else:
        port_visited[src_port_idx]=True

    dst_ports=[]
    if src_port in port_net_dict:
        if from_out_port:
            dst_ports=net_list[port_net_dict[src_port]]['in_ports']
        else:
            dst_ports=[net_list[port_net_dict[src_port]]['out_port']]
    for dst_port in dst_ports:
        # New relations: src_ports' scale params are transitive to dst_ports
        add_scale_param_eqns(src_port,dst_port,transitive_closure_relns)
    for dst_port in dst_ports:
        #DFS
        transitive_dfs(dst_port,port_list,net_list,port_net_dict, \
                       port_visited,transitive_closure_relns,from_out_port)

def solve1_transitive_closure_dfs(port_list,net_list,out_port_net_dict):
    '''
    DFS algorithm to infer microarchitecture port scale parameters based on boundary conditions at
    architecture buffer ports
    '''
    transitive_closure_relns=[]
    port_visited=[False]*len(port_list)

    for src_port in port_list:
        transitive_dfs(src_port,port_list,net_list,out_port_net_dict, \
                       port_visited,transitive_closure_relns,from_out_port=True)

    return transitive_closure_relns