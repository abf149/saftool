from util.helper import info,warn,error
import util.helper as helper
import safinfer,safmodel,util.safsearch_io as safsearch_io
'''
from util import safmodel_core as safcore, \
                 safmodel_io as safio, \
                 safinfer_io
'''

def opening_remark():
    info(">> SAFsearch",also_stdout=True)  

def setup(taxo_script_lib_list,characterization_path_list, \
          model_script_lib_list):
    safmodel.setup(taxo_script_lib_list,characterization_path_list, \
                   model_script_lib_list,require_taxo=True)

def log_config(do_logging,log_fn):
    print("logging:",do_logging)
    helper.do_log=do_logging
    if do_logging:
        helper.log_init(log_fn)

def closing_remark():
    warn("<< Done, SAFsearch",also_stdout=True)

if __name__=="__main__":
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
    taxo_script_lib_list, \
    taxo_uarch, \
    comp_in, \
    arch_out_path, \
    comp_out_path, \
    user_attributes, \
    characterization_path_list, \
    model_script_lib_list = safsearch_io.parse_args()

    log_config(do_logging,log_fn)
    opening_remark()
    # Safinfer/safmodel setup
    setup(taxo_script_lib_list,characterization_path_list, \
          model_script_lib_list)
    closing_remark()