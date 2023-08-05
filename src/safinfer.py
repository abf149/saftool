'''SAFinfer tool infers microarchitecture topology from Sparseloop configuration files'''

import util.sparseloop_config_processor as sl_config
from util.taxonomy.serializableobject import *
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *
from util.taxonomy.arch import *
import argparse
yaml.Dumper.ignore_aliases = lambda *args : True
default_ruleset_list = ['base_ruleset', \
                        'primitive_md_parser_ruleset', \
                        'format_uarch_ruleset'] # 'skipping_uarch_ruleset'

'''CLI and file dump routines'''
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
'''Routines to build and solve SAF uarch inference problem'''
def build_saf_uarch_inference_problem(arch, sparseopts, prob, mapping, reconfigurable_arch, bind_out_path):
    '''
    Consume the raw Sparseloop arch/sparseopts/prob/mapping, and use the abstractions defined in 
    util.taxonomy to build a SAF microarchitecture topology with holes representing the
    unsolved-for portions of the SAF microarchitecture. This constitutes a "problem description"
    for the solver.\n\n

    Arguments:\n
    - arch: Sparseloops accelerator architecture\n
    - sparseopts: Sparseloops sparse optimizations\n
    - prob: Sparseloops tensor problem description\n
    - mapping: Sparseloops mapping description\n
    - reconfigurable_arch: True if architecture is reconfigurable based on mapping\n
    - bind_out_path: YAML output filepath for dumping format and action bindings\n\n

    Returns:\n
    - taxo_arch: SAF microarchitecture topology with holes (problem description for solver)
    '''
    # - Compute SAF microarchitecture bindings to architectural buffers    
    print("\nBuilding the SAF microarchitecture inference problem.")
    print("- Computing SAF microarchitecture bindings to architectural buffers.")
    fmt_iface_bindings=[]
    skip_bindings=[]
    data_space_dict_list=[]
    if not reconfigurable_arch:
        # "Typical" case: fixed architecture with sparseopts
        pass
    else:
        # "Special" case: reconfigurable architecture tuned for problem and mapping
        fmt_iface_bindings, \
        skip_bindings, \
        data_space_dict_list = sl_config.compute_reconfigurable_arch_bindings(arch,sparseopts,prob,mapping)

    # - Dump bindings
    print("  => Done. Dumping bindings to",bind_out_path)
    dump_bindings(bind_out_path,fmt_iface_bindings,skip_bindings)

    # - Create microarchitecture topology with dummy buffers interfaced to SAF microarchitectures which contain holes

    # Create a data structure to represent architectural buffers and SAF microarchitectures
    # Problem- and mapping-independent, given fmt_iface_bindings, skip_bindings
    # and data_space_dict_list have already been computed
    print("- Realizing microarchitecture with topological holes, based on bindings.\n")
    taxo_arch=topology_with_holes_from_bindings(arch, fmt_iface_bindings, skip_bindings, data_space_dict_list)

    return taxo_arch
def solve_saf_uarch_inference_problem(taxo_arch, saftaxolib, ruleset_names=default_ruleset_list):
    '''
    Trigger SAF microarchitecture solver against an input
    problem description, which is a SAF microarchitecture
    topology with holes.\n\n

    Arguments:\n
    - taxo_arch -- SAF microarchitecture topology with holes (problem description for solver)\n
    - saftaxolib -- directory path to SAF microarchitecture inference rules libraries\n\n

    Returns:\n
    - result -- solver results structure, including success/failure and SAF microarchitecture taxonomy.
    '''

    print("\nSolving the SAF microarchitecture inference problem.\n")    
    print("- Loading rules engine.")
    # Extend rulesnames with SAF taxonomic ruleset library directory path
    # prefix to get list of ruleset paths, then load rulesets into RulesEngine
    # and solve for SAF microarchitecture topology
    ruleset_full_paths=[saftaxolib+ruleset for ruleset in ruleset_names]
    rules_engine = RulesEngine(ruleset_full_paths)
    rules_engine.preloadRules()
    print("- Solving.")    
    result=rules_engine.run(taxo_arch)
    
    return result

'''
main() - build and solve SAF microarchitecture inference problem
based on CLI arguments and dump the inferred SAF microarchitecture
topology to the YAML file at --topology-out
'''
if __name__=="__main__":

    # Parse CLI arguments
    arch, \
    mapping, \
    prob, \
    sparseopts, \
    reconfigurable_arch, \
    bind_out_path, \
    topo_out_path, \
    saftaxolib = parse_args()

    # Build and solve the SAF microarchitecture inference problem:
    taxo_arch = build_saf_uarch_inference_problem(arch, \
                                                  sparseopts, \
                                                  prob, \
                                                  mapping, \
                                                  reconfigurable_arch, \
                                                  bind_out_path)
    result = solve_saf_uarch_inference_problem(taxo_arch, saftaxolib)

    # Success: dump
    # Fail: exit
    outcome=result[0]
    inferred_arch=result[-1][-1]
    if outcome:
        print("  => SUCCESS")
        dump_saf_uarch_topology(inferred_arch,topo_out_path)
    else:
        print("  => FAILURE")