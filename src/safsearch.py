from util.helper import info,warn,error
import util.helper as helper
import safinfer,safmodel,util.safsearch_io as safsearch_io,util.safsearch_core as safsearch_core
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
    safsearch_io.log_control(do_logging)
    safsearch_io.enable_stdout()
    safsearch_io.enable_stderr()
    if do_logging:
        helper.log_init(log_fn)

def pipeline(arch, \
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
             safinfer_user_attributes, \
             safmodel_user_attributes, \
             characterization_path_list, \
             model_script_lib_list):
    
    final_configs_dict=safsearch_core.build_taxonomic_search_space(arch, \
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
                                                         safinfer_user_attributes, \
                                                         characterization_path_list, \
                                                         model_script_lib_list)
    
    #print("final_configs_dict:",final_configs_dict)


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
    safinfer_user_attributes, \
    safmodel_user_attributes, \
    characterization_path_list, \
    model_script_lib_list, = safsearch_io.parse_args()

    #print(safinfer_user_attributes)
    #assert(False)

    log_config(do_logging,log_fn)
    opening_remark()
    setup(taxo_script_lib_list,characterization_path_list, \
          model_script_lib_list)
    pipeline(arch, \
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
             safinfer_user_attributes, \
             safmodel_user_attributes, \
             characterization_path_list, \
             model_script_lib_list)
    closing_remark()