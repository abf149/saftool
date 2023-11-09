'''SAFinfer core library - build and solve SAF microarchitecture inference problem from Sparseloop inputs'''
from util import sparseloop_config_processor as sl_config, safinfer_io as safio
from solver.solve import Solver
from solver.build import build_taxonomic_arch_and_safs_from_bindings
from util.helper import info,warn,error

'''Constants - default list of ruleset names to apply to SAF microarchitecture topology inference'''
'''
default_ruleset_list = ['base_ruleset', \
                        'format_uarch_ruleset', \
                        'address_primitives_ruleset', \
                        'gating_ruleset', \
                        'skipping_uarch_ruleset']
'''

default_ruleset_list = ['base_ruleset', \
                        'format_uarch_ruleset', \
                        'address_primitives_ruleset', \
                        'gating_ruleset', \
                        'skipping_uarch_ruleset']

'''Routines - build and solve SAF microarchitecture inference problem'''
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
    info("\nBuilding the SAF microarchitecture inference problem.")
    info("- Computing SAF microarchitecture bindings to architectural buffers.")
    fmt_iface_bindings=[]
    skip_bindings=[]
    data_space_dict_list=[]
    if not reconfigurable_arch:
        # "Typical" case: fixed architecture with sparseopts

        fmt_iface_bindings, \
        skip_bindings, \
        dtype_list, _, _ = sl_config.compute_fixed_arch_bindings(arch,sparseopts)
    else:
        # "Special" case: reconfigurable architecture tuned for problem and mapping
        fmt_iface_bindings, \
        skip_bindings, \
        data_space_dict_list = sl_config.compute_reconfigurable_arch_bindings(arch,sparseopts,prob,mapping)
        dtype_list=list(data_space_dict_list.keys())

    # - Dump bindings
    info("  => Done. Dumping bindings to",bind_out_path)
    safio.dump_bindings(bind_out_path,fmt_iface_bindings,skip_bindings)

    # - Create microarchitecture topology with dummy buffers interfaced to SAF microarchitectures which contain holes

    # Create a data structure to represent architectural buffers and SAF microarchitectures
    # Problem- and mapping-independent, given fmt_iface_bindings, skip_bindings
    # and data_space_dict_list have already been computed
    info("- Realizing microarchitecture with topological holes, based on bindings.\n")
    return build_taxonomic_arch_and_safs_from_bindings(arch, fmt_iface_bindings, skip_bindings, dtype_list)
def solve_saf_uarch_inference_problem(taxo_arch, saflib_path, ruleset_names=default_ruleset_list):
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

    info("\nSolving the SAF microarchitecture inference problem.\n")    
    info("- Loading rules engine.")
    # Extend rulesnames with SAF taxonomic ruleset library directory path
    # prefix to get list of ruleset paths, then load rulesets into RulesEngine
    # and solve for SAF microarchitecture topology
    ruleset_full_paths=[saflib_path+ruleset for ruleset in ruleset_names]
    rules_engine = Solver(ruleset_full_paths)
    rules_engine.preloadRules()
    info("\n\n- Solving.")    
    result=rules_engine.run(taxo_arch)
    
    return result