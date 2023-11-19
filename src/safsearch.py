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
             safsearch_user_attributes, \
             safinfer_user_attributes, \
             safmodel_user_attributes, \
             characterization_path_list, \
             model_script_lib_list, \
             log_taxo_component_search_space_discovery,
             log_global_search_safinfer, \
             log_global_search_safmodel, \
             dump_best, \
             load_best, \
             top_N, \
             model_top_x, \
             remark=False):
    if remark:
        opening_remark()
    if dump_best:
        warn(":: --dump-best selected; SAFsearch pipeline will terminate after search completes.")
    elif load_best:
        warn(":: --load-best selected; SAFsearch will skip search and load best configuration from file.")

    if not dump_best:
        if model_top_x != 0:
            if model_top_x > top_N-1:
                error("Size of top-N search-result ranking is",str(top_N), \
                      "(--top-N)","which is too small to synthesize a model for the top -", \
                        str(model_top_x),"search result (--model-top-x)")
                info("Terminating.")
                assert(False)
            warn(":: Model synthesis will target the top - ", \
                 str(model_top_x),"th solution (--model-top-x =",str(model_top_x),")")

    global_search_space=None
    search_result=None
    best_config=None

    if not load_best:
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
                                                                        safsearch_user_attributes, \
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
                                                    log_global_search_safmodel, \
                                                    top_N)
        
        best_config = {
            "global_search_space":global_search_space,
            "search_result":search_result
        }
    else:
        # --load-best skips search and loads saved search result
        best_config=safsearch_io.load_best_config()
        global_search_space=best_config['global_search_space']
        search_result=best_config['search_result']

    if dump_best:
        # --dump-best skips post-search steps and dumps search result to file
        safsearch_io.dump_best_config(best_config)
        return

    safsearch_io.export_artifacts_from_search_result(best_config, \
                                                       top_N, \
                                                        model_top_x, \
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
    safsearch_user_attributes, \
    safinfer_user_attributes, \
    safmodel_user_attributes, \
    characterization_path_list, \
    model_script_lib_list, \
    dump_best, \
    load_best, \
    top_N, \
    model_top_x, \
    log_taxo_component_search_space_discovery, \
    log_global_search_safinfer, \
    log_global_search_safmodel = safsearch_io.parse_args()

    # you don't have to use dump_best or load_best,
    # but they are mutually-exclusive
    assert((not (dump_best and load_best)))

    #log_taxo_component_search_space_discovery=False
    #log_global_search_safinfer=False
    #log_global_search_safmodel=False

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
             safsearch_user_attributes, \
             safinfer_user_attributes, \
             safmodel_user_attributes, \
             characterization_path_list, \
             model_script_lib_list, \
             log_taxo_component_search_space_discovery, \
             log_global_search_safinfer, \
             log_global_search_safmodel, \
             dump_best, \
             load_best, \
             top_N, \
             model_top_x)
    closing_remark()