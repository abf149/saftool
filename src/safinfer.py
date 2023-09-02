'''SAFinfer - tool to build and solve SAF microarchitecture inference problem from Sparseloop inputs'''
from util import safinfer_core as safcore, safinfer_io as safio
import util.helper as helper
import os

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
    saflib, \
    do_logging,\
    log_fn = safio.parse_args()

    print("logging:",do_logging)
    helper.do_log=do_logging
    if do_logging:
        helper.log_init(log_fn)    
    print("reconfigurable_arch:",reconfigurable_arch)

    # Build and solve the SAF microarchitecture inference problem:
    taxo_arch = safcore.build_saf_uarch_inference_problem(arch, \
                                                  sparseopts, \
                                                  prob, \
                                                  mapping, \
                                                  reconfigurable_arch, \
                                                  bind_out_path)

    result = safcore.solve_saf_uarch_inference_problem(taxo_arch, saflib)

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