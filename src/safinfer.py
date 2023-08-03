'''SAFinfer tool infers microarchitecture topology from Sparseloop configuration files'''

import util.sparseloop_config_processor as sl_config
from util.taxonomy.serializableobject import *
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *
from util.taxonomy.arch import *
import argparse

yaml.Dumper.ignore_aliases = lambda *args : True

def dump_bindings(bind_out_path,fmt_iface_bindings,skip_bindings):
    print("- Saving to",bind_out_path)
    with open(bind_out_path, 'w') as fp:
        bindings_data_structure={"fmt_iface_bindings":fmt_iface_bindings, \
                                 "skip_bindings":skip_bindings}
        yaml.dump(bindings_data_structure,fp, default_flow_style=False)    

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--saftaxolib',default='saftaxolib/')
    parser.add_argument('-i','--dir-in',default='')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml')
    parser.add_argument('-m','--map',default='ref_input/map.yaml')
    parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml')
    parser.add_argument('-o','--dir-out',default='')
    parser.add_argument('-b','--binding-out',default='ref_output/bindings.yaml')
    parser.add_argument('-t','--topology-out',default='ref_output/new_arch.yaml')
    parser.add_argument('-r','--reconfigurable-arch',default=False)    
    args = parser.parse_args()

    # Parse the CLI arguments
    print("SAFinfer.\n")    
    print("Parsing input files:")    
    if len(args.dir_in)>0:
        print("- arch:",args.dir_in+'arch.yaml')
        arch=sl_config.load_config_yaml(args.dir_in+'arch.yaml')
        print("- map:",args.dir_in+'map.yaml')
        mapping=sl_config.load_config_yaml(args.dir_in+'map.yaml')
        print("- prob:",args.dir_in+'prob.yaml')
        prob=sl_config.load_config_yaml(args.dir_in+'prob.yaml')
        print("- sparseopts:",args.dir_in+'sparseopts.yaml')
        sparseopts=sl_config.load_config_yaml(args.dir_in+'sparseopts.yaml')        
    else:    
        print("- arch:",args.arch)
        arch=sl_config.load_config_yaml(args.arch)
        print("- map:",args.map)
        mapping=sl_config.load_config_yaml(args.map)
        print("- prob:",args.prob)
        prob=sl_config.load_config_yaml(args.prob)
        print("- sparseopts:",args.sparseopts)
        sparseopts=sl_config.load_config_yaml(args.sparseopts)

    # Check reconfigurable-arch so we know whether to crash (if True)
    if not args.reconfigurable_arch:
        print("- fixed arch (reconfigurable-arch == False)")
    else:
        print("- ERROR reconfigurable arch not yet supported")
        #assert(False)

    # Build the microarchitecture inference problem:
    # - Compute SAF microarchitecture bindings to architectural buffers
    print("\nBuilding the SAF microarchitecture inference problem.")
    print("- Computing SAF microarchitecture bindings to architectural buffers.")
    fmt_iface_bindings=[]
    skip_bindings=[]
    data_space_dict_list=[]
    if not args.reconfigurable_arch:
        # "Typical" case: fixed architecture with sparseopts
        pass
    else:
        # "Special" case: reconfigurable architecture tuned for problem and mapping
        fmt_iface_bindings, \
        skip_bindings, \
        data_space_dict_list = sl_config.compute_reconfigurable_arch_bindings(arch,sparseopts,prob,mapping)

    # - Dump bindings
    bind_out_path=args.binding_out
    print("  => Done. Dumping bindings to",bind_out_path)    
    if len(args.dir_out) > 0:
        bind_out_path=args.dir_out+'bindings.yaml'
        topo_out_path=args.dir_out+'new_arch.yaml'
    dump_bindings(bind_out_path,fmt_iface_bindings,skip_bindings)

    # - Create microarchitecture topology with dummy buffers interfaced to SAF microarchitectures which contain holes

    # Create a data structure to represent architectural buffers and SAF microarchitectures
    # Problem- and mapping-independent, given fmt_iface_bindings, skip_bindings
    # and data_space_dict_list have already been computed
    print("- Realizing microarchitecture with topological holes, based on bindings.\n")
    taxo_arch=topology_with_holes_from_bindings(arch, fmt_iface_bindings, skip_bindings, data_space_dict_list)

    # Solve the SAF microarchitecture inference problem
    print("\nSolving the SAF microarchitecture inference problem.\n")    
    print("- Loading rules engine.")
    rules_engine = RulesEngine([args.saftaxolib+'base_ruleset', \
                                args.saftaxolib+'primitive_md_parser_ruleset', \
                                args.saftaxolib+'format_uarch_ruleset'])
                                #args.saftaxolib+'skipping_uarch_ruleset']) # No longer needed
    rules_engine.preloadRules()
    print("- Solving.")    
    result=rules_engine.run(taxo_arch)
    outcome=result[0]

    # Success: dump
    # Fail: exit
    topo_out_path=args.topology_out
    if outcome:
        print("  => SUCCESS")
        print("- Dumping inferred SAF microarchitecture topology to",topo_out_path,"...")
        inferred_arch=result[-1][-1]
        inferred_arch.dump(topo_out_path)
    else:
        print("  => FAILURE")