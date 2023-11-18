from search.taxonomic.build.component import build_per_component_taxonomic_search_space
from search.taxonomic.build.global_space import build_global_taxonomic_search_space
from search.search import search
from util.helper import info,warn,error

def build_taxonomic_search_space(arch, \
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
                                log_taxo_component_search_space_discovery=False, \
                                top_lvl_comp_cnt_sanity_limit=100, \
                                comp_tree_depth_sanity_limit=100):
    
    info(":: Building taxonomic search-space...",also_stdout=True)
    per_comp_search_space=build_per_component_taxonomic_search_space(arch, \
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
                                                                     log_taxo_component_search_space_discovery, \
                                                                     top_lvl_comp_cnt_sanity_limit= \
                                                                     top_lvl_comp_cnt_sanity_limit, \
                                                                     comp_tree_depth_sanity_limit= \
                                                                     comp_tree_depth_sanity_limit)

    top_lvl_comp_list, \
    num_top_lvl_comps, \
    per_comp_space_size_dict, \
    global_space_size = build_global_taxonomic_search_space(per_comp_search_space)

    warn(":: => Done, building taxonomic search-space.",also_stdout=True)
    return {
                "per_comp_search_space":per_comp_search_space,
                "top_lvl_comp_list":top_lvl_comp_list,
                "num_top_lvl_comps":num_top_lvl_comps,
                "per_comp_space_size_dict":per_comp_space_size_dict,
                "global_space_size":global_space_size
           }

def global_search(global_search_space, \
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
                    log_global_search_safmodel):
    info(":: Searching...",also_stdout=True)

    search_point_id_to_config_list, \
    search_point_id_to_result_list, \
    best_search_point_id, \
    best_objective, \
    best_state, \
    best_global_search_point, \
    top_N_tracker = search(global_search_space, \
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
    
    warn(":: => Done, searching...",also_stdout=True)
    return {
                "search_point_id_to_config_list":search_point_id_to_config_list,
                "search_point_id_to_result_list":search_point_id_to_result_list,
                "best_search_point_id":best_search_point_id,
                "best_objective":best_objective,
                "best_state":best_state,
                "best_global_search_point":best_global_search_point,
                "top_N_tracker":top_N_tracker
            }


def export_artifacts_from_search_result(search_result, \
                                        global_search_space, \
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
                                        log_global_search_safmodel):
    
    pass