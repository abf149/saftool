'''SAFinfer IO library - CLI argparse and YAML dump routines'''
from collections import deque
import util.sparseloop_config_processor as sl_config, yaml, argparse
from util.helper import info,warn,error
import util.notation.predicates as p_
import solver.model.build_support.abstraction as ab
import saflib.microarchitecture.TaxoRegistry as tr_

'''Config - condition the format of YAML file dumps'''
yaml.Dumper.ignore_aliases = lambda *args : True

'''Load & parse taxonomic libraries'''
def load_parse_taxo_libs(taxo_script_lib_list):
    #print(taxo_script_lib_list)
    # Parse taxoscript
    import glob,yaml
    import parser.taxo_parser_core as tp_
    lib_filepath_list=[]
    for taxo_script_lib in taxo_script_lib_list:
        lib_filepath_list.extend(glob.glob(taxo_script_lib))
    info("Parsing taxoscript libraries (",len(lib_filepath_list),")...")
    #print(lib_filepath_list)
    # First pass - parse primitives
    for idx,script_dict in enumerate([sl_config.load_config_yaml(fn) for fn in lib_filepath_list]):
        #print(idx)
        lib_filepath=lib_filepath_list[idx]
        info("-",lib_filepath)
        _, _=tp_.parse_taxoscript(script_dict,primitives_only=True)
    # Second pass - parse components
    for idx,script_dict in enumerate([sl_config.load_config_yaml(fn) for fn in lib_filepath_list]):
        #print(idx)
        lib_filepath=lib_filepath_list[idx]
        info("-",lib_filepath)
        _, _=tp_.parse_taxoscript(script_dict,components_only=True)
    warn("=> Done,")

'''CLI argparse'''
def parse_args():
    '''
    Parse CLI arguments.\n\n

    Arguments: None\n\n

    Returns:\n
    - arch -- Sparseloop architecture\n
    - mapping -- Sparseloop mapping\n
    - prob -- Sparseloop problem\n
    - sparseopts -- Sparseloop sparse optimizations
    - reconfigurable_arch -- True if arch reconfigurable for prob/mapping, False if fixed arch
    - bind_out_path -- output filepath for dumping format and action bindings
    - topo_out_path -- output filepath for dumping inferred SAF microarchitecture topology
    - saftaxolib -- SAF taxonomy library directory
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--saftaxolib',default='saflib/rulesets/taxo/')
    parser.add_argument('-i','--dir-in',default='')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml')
    parser.add_argument('-m','--map',default='ref_input/map.yaml')
    parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml')
    parser.add_argument('-o','--dir-out',default='')
    parser.add_argument('-b','--binding-out',default='ref_output/bindings.yaml')
    parser.add_argument('-t','--taxo-script-lib',action='append',default=['saflib/microarchitecture/taxoscript/*.yaml'])
    parser.add_argument('-T','--topology-out',default='ref_output/new_arch.yaml')
    parser.add_argument('-r', '--reconfigurable-arch', action='store_true')
    parser.add_argument('-L','--log', action='store_true')
    parser.add_argument('-f','--log-file',default='./safinfer.log')
    args = parser.parse_args()

    # Parse the CLI arguments
    info("SAFinfer.\n")    
    do_logging=args.log
    info("Parsing input files:")    
    if len(args.dir_in)>0:
        info("- arch:",args.dir_in+'arch.yaml')
        arch=sl_config.load_config_yaml(args.dir_in+'arch.yaml')
        info("- map:",args.dir_in+'map.yaml')
        mapping=sl_config.load_config_yaml(args.dir_in+'map.yaml')
        info("- prob:",args.dir_in+'prob.yaml')
        prob=sl_config.load_config_yaml(args.dir_in+'prob.yaml')
        info("- sparseopts:",args.dir_in+'sparseopts.yaml')
        sparseopts=sl_config.load_config_yaml(args.dir_in+'sparseopts.yaml')        
    else:    
        info("- arch:",args.arch)
        arch=sl_config.load_config_yaml(args.arch)
        info("- map:",args.map)
        mapping=sl_config.load_config_yaml(args.map)
        info("- prob:",args.prob)
        prob=sl_config.load_config_yaml(args.prob)
        info("- sparseopts:",args.sparseopts)
        sparseopts=sl_config.load_config_yaml(args.sparseopts)

    # Check reconfigurable-arch so we know whether to crash (if True)
    if not args.reconfigurable_arch:
        info("- fixed arch (reconfigurable-arch == False)")
    else:
        error("- ERROR reconfigurable arch not yet supported")
        #assert(False)

    bind_out_path=args.binding_out
    topo_out_path=args.topology_out
    if len(args.dir_out) > 0:
        bind_out_path=args.dir_out+'bindings.yaml'
        topo_out_path=args.dir_out+'new_arch.yaml'

    return arch, \
           mapping, \
           prob, \
           sparseopts, \
           args.reconfigurable_arch, \
           bind_out_path, \
           topo_out_path, \
           args.saftaxolib, \
           do_logging, \
           args.log_file, \
           args.taxo_script_lib

'''Binding & SAF microarchitecture topology YAML dumps'''
def dump_bindings(bind_out_path,fmt_iface_bindings,skip_bindings):
    '''
    Dump format interface bindings and skip action bindings to YAML file.\n\n
    Arguments:\n
    - bind_out_path -- YAML output file path\n
    - fmt_iface_bindings -- format interface bindings structure\n
    - skip_bindings -- skip action bindings structure\n\n

    Side-effects: dump the following data-structure to file\n\n

    {"fmt_iface_bindings":fmt_iface_bindings,"skip_bindings":skip_bindings}\n\n

    Returns: None
    '''

    info("- Saving to",bind_out_path)
    with open(bind_out_path, 'w') as fp:
        bindings_data_structure={"fmt_iface_bindings":fmt_iface_bindings, \
                                 "skip_bindings":skip_bindings}
        yaml.dump(bindings_data_structure,fp, default_flow_style=False)    
def dump_saf_uarch_topology(inferred_arch,topo_out_path):
    '''
    Dump inferred SAF microarchitecture topology data structure to YAML file.\n\n

    Arguments:\n
    - inferred_arch: inferred SAF microarchitecture\n
    - topo_out_path: YAML output filepath\n\n

    Returns: None
    '''
    info("- Dumping inferred SAF microarchitecture topology to",topo_out_path,"...")
    inferred_arch.dump(topo_out_path)
    with open(topo_out_path+".pretty","w") as fp:
        fp.write(sprettyprint_taxo_uarch(inferred_arch))

'''Transform between monolithic SAFinfer internal representation vs modular representation'''
def taxo_uarch_monolithic_to_modular(taxo_uarch):
    comp_list=[]
    def refactor_bfs(obj, comp_list):
        # Queue for BFS
        # (Taxonomic microarchitecture object, object uri)
        queue = deque([(obj,obj.getId())])
        
        # Set to keep track of visited nodes
        visited = set()
        
        while queue:
            # Dequeue a node from the front
            current_obj,obj_uri = queue.popleft()
            subcomponent_list=[]

            # If the object is not a Primitive
            if p_.isComponentOrArchitecture(current_obj):
                for new_obj in current_obj.getTopology().getComponentList():
                    new_obj_uri=ab.uri(obj_uri,new_obj.getId())
                    # If the new_obj has not been visited
                    if new_obj_uri not in visited:
                        # Mark the node as visited and enqueue it
                        visited.add(new_obj_uri)
                        subcomponent_list.append(new_obj.getId())
                        queue.append((new_obj,new_obj_uri))
                        
                # Replace subcomponents with references
                topology=current_obj.getTopology()
                topology.setComponentList(subcomponent_list)
                current_obj.setTopology(topology)

            current_obj.setId(obj_uri)
            comp_list.append(current_obj)

    refactor_bfs(taxo_uarch, comp_list)

    return comp_list

'''Pretty-print routines'''

def sprettyprint_taxo_uarch(taxo_uarch):
    res=""
    modular_uarch=taxo_uarch_monolithic_to_modular(taxo_uarch)
    comp_categories={tum.getId():tum.getCategory()for tum in modular_uarch}

    def spp_taxo_uarch_module(tum,res,comp_categories):
        res+=tum.getId()+"("+tum.getCategory()+"):\n"
        attrs=tum.getAttributes()
        if len(attrs)>0:
            res+="- Attributes:\n"
            for attr_ in attrs:
                if type(attr_).__name__ == "list" and type(attr_[0]).__name__ == "FormatType":
                    res+="  - (fibertree) " + str([rank.getValue() for rank in attr_]) + "\n"
                elif type(attr_).__name__ == "FormatType":
                    res+="  - (format) " + str(attr_.getValue()) + "\n"
                else:
                    res+="  - " + str(attr_) + "\n"
        if p_.isComponentOrArchitecture(tum):
            topology=tum.getTopology()
            comp_list=topology.getComponentList()
            net_list=topology.getNetList()
            if len(comp_list)>0:
                res+="- Components:\n"
                for comp in comp_list:
                    res+="  - "+comp+"("+comp_categories[ab.uri(tum.getId(),comp)]+")\n"
            if len(net_list)>0:
                res+="- Nets:\n"
                for net in net_list:
                    res+=" - "+str(net.getPortIdList())+"\n"

        return res

    
    for taxo_uarch_module in modular_uarch:
        res=spp_taxo_uarch_module(taxo_uarch_module,res,comp_categories)
        res+="\n\n"

    return res