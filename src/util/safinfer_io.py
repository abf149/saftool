'''SAFinfer IO library - CLI argparse and YAML dump routines'''
import util.sparseloop_config_processor as sl_config, yaml, argparse

'''Config - condition the format of YAML file dumps'''
yaml.Dumper.ignore_aliases = lambda *args : True

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
    parser.add_argument('-l','--saftaxolib',default='saftaxolib/')
    parser.add_argument('-i','--dir-in',default='')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml')
    parser.add_argument('-m','--map',default='ref_input/map.yaml')
    parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml')
    parser.add_argument('-o','--dir-out',default='')
    parser.add_argument('-b','--binding-out',default='ref_output/bindings.yaml')
    parser.add_argument('-t','--topology-out',default='ref_output/new_arch.yaml')
    parser.add_argument('-r', '--reconfigurable-arch', action='store_true')
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
           args.saftaxolib

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

    print('fmt_iface_bindings:',fmt_iface_bindings)
    print('skip_bindings:',skip_bindings)
    print("- Saving to",bind_out_path)
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
    print("- Dumping inferred SAF microarchitecture topology to",topo_out_path,"...")
    inferred_arch.dump(topo_out_path)