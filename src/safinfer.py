'''SAFinfer - tool to build and solve SAF microarchitecture inference problem from Sparseloop inputs'''
from core import safinfer_core as safcore, \
                 safinfer_io as safio
from core.helper import info,warn,error
import core.helper as helper
import os

def opening_remark():
    info(">> SAFinfer",also_stdout=True)  

def log_config(do_logging,log_fn):
    print("logging:",do_logging)
    helper.enable_log=do_logging
    if do_logging:
        helper.log_init(log_fn)

def setup(taxo_script_lib):
    warn(":: Setup",also_stdout=True)
    # Load taxonomic library
    safio.load_parse_taxo_libs(taxo_script_lib)
    warn(":: => Done, setup",also_stdout=True)

def pipeline(arch,mapping,prob,sparseopts,reconfigurable_arch,bind_out_path,saflib_path,user_attributes,remarks=False):
    if remarks:
        opening_remark() 
    info("reconfigurable_arch:",reconfigurable_arch,also_stdout=True)

    warn(":: Taxonomic inference",also_stdout=True)

    # Build and solve the SAF microarchitecture inference problem:
    taxo_arch = safcore.build_saf_uarch_inference_problem(arch, \
                                                          sparseopts, \
                                                          prob, \
                                                          mapping, \
                                                          reconfigurable_arch, \
                                                          bind_out_path, \
                                                          user_attributes=user_attributes)

    if remarks:
        closing_remark()
    return safcore.solve_saf_uarch_inference_problem(taxo_arch, \
                                                     saflib_path, \
                                                     user_attributes=user_attributes)

def handle_outcome(result,topo_out_path):
    # Success: dump
    # Fail: exit
    #print(result[-1][0].getTopology().getComponentList()[-1])
    #print(result[0])
    outcome=result['outcome']
    inferred_arch=result['component_iterations'][-1]
    uri=result['uri']
    failure_comp=result['failure_comp']
    if outcome:
        warn("  => SUCCESS",also_stdout=True)
        safio.dump_saf_uarch_topology(inferred_arch,topo_out_path)
    else:
        error("  => FAILURE",also_stdout=True)
        safio.dump_saf_uarch_topology(inferred_arch,topo_out_path + ".fail")
        info("Failure component:",also_stdout=True)
        info("- Component:",uri,also_stdout=True)
        info("- Attributes:",failure_comp.getAttributes(),also_stdout=True)
    warn(":: => Done, taxonomic inference",also_stdout=True)

def closing_remark():
    warn("<< Done, SAFinfer",also_stdout=True)

''' main() - build and solve SAF microarchitecture inference problem
based on CLI arguments and dump the inferred SAF microarchitecture
topology to the YAML file at --topology-out
'''
def main():
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
    taxo_script_lib, \
    user_attributes = safio.parse_args()

    log_config(do_logging,log_fn)
    opening_remark()
    setup(taxo_script_lib)
    result=pipeline(arch,mapping,prob,sparseopts,reconfigurable_arch,bind_out_path, \
                    saflib_path, user_attributes)
    #print(result)
    handle_outcome(result,topo_out_path)
    closing_remark()

if __name__=="__main__" and not os.getenv("SPHINX_BUILD"):
    main()