'''SAFinfer - tool to build and solve SAF microarchitecture inference problem from Sparseloop inputs'''
from util import safinfer_core as safcore, \
                 safinfer_io as safio
from util.helper import info,warn,error
import util.helper as helper

def opening_remark():
    info(">> SAFinfer",also_stdout=True)  

def log_config(do_logging,log_fn):
    print("logging:",do_logging)
    helper.do_log=do_logging
    if do_logging:
        helper.log_init(log_fn)

def setup(taxo_script_lib):
    warn(":: Setup",also_stdout=True)
    # Load taxonomic library
    safio.load_parse_taxo_libs(taxo_script_lib)
    warn(":: => Done, setup",also_stdout=True)

def pipeline(arch,mapping,prob,sparseopts,reconfigurable_arch,bind_out_path, \
             saflib_path,taxo_script_lib): 
    info("reconfigurable_arch:",reconfigurable_arch,also_stdout=True)

    warn(":: Taxonomic inference",also_stdout=True)

    # Build and solve the SAF microarchitecture inference problem:
    taxo_arch = safcore.build_saf_uarch_inference_problem(arch, \
                                                          sparseopts, \
                                                          prob, \
                                                          mapping, \
                                                          reconfigurable_arch, \
                                                          bind_out_path)

    return safcore.solve_saf_uarch_inference_problem(taxo_arch, saflib_path)

def handle_outcome(result):
    # Success: dump
    # Fail: exit
    outcome=result[0]
    inferred_arch=result[-1][-1]
    if outcome:
        print("  => SUCCESS")
        safio.dump_saf_uarch_topology(inferred_arch,topo_out_path)
    else:
        print("  => FAILURE")
        safio.dump_saf_uarch_topology(inferred_arch,topo_out_path + ".fail")
    warn(":: => Done, taxonomic inference",also_stdout=True)

def closing_remark():
    warn("<< Done, SAFinfer",also_stdout=True)

''' main() - build and solve SAF microarchitecture inference problem
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
    saflib_path, \
    do_logging,\
    log_fn, \
    taxo_script_lib = safio.parse_args()

    log_config(do_logging,log_fn)
    opening_remark()
    setup(taxo_script_lib)
    result=pipeline(arch,mapping,prob,sparseopts,reconfigurable_arch,bind_out_path, \
                    saflib_path,taxo_script_lib)
    handle_outcome(result)
    closing_remark()