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
             model_script_lib_list, \
             log_taxo_component_search_space_discovery,
             log_global_search_safinfer, \
             log_global_search_safmodel, \
             remark=False):
    if remark:
        opening_remark()
    global_search_space=safsearch_core.build_taxonomic_search_space(arch, \
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
                                                                    model_script_lib_list, \
                                                                    log_taxo_component_search_space_discovery)
    search_result=safsearch_core.global_search(global_search_space, \
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
                                                model_script_lib_list, \
                                                log_global_search_safinfer, \
                                                log_global_search_safmodel)
    
    safsearch_core.export_artifacts_from_search_result(global_search_space, \
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
                                                        model_script_lib_list, \
                                                        log_global_search_safinfer, \
                                                        log_global_search_safmodel)
    
    if remark:
        closing_remark()

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

    log_taxo_component_search_space_discovery=False
    log_global_search_safinfer=False
    log_global_search_safmodel=False

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
             model_script_lib_list, \
             log_taxo_component_search_space_discovery, \
             log_global_search_safinfer, \
             log_global_search_safmodel)
    closing_remark()