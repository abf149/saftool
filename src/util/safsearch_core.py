import search.taxonomic.build.component as bc_
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
    top_lvl_comp_cnt_sanity_limit=100, \
    comp_tree_depth_sanity_limit=100):
    
    info(":: Building taxonomic search-space...",also_stdout=True)
    per_comp_search_space=bc_.build_per_component_taxonomic_search_space(arch, \
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
                                                                         top_lvl_comp_cnt_sanity_limit= \
                                                                            top_lvl_comp_cnt_sanity_limit, \
                                                                         comp_tree_depth_sanity_limit= \
                                                                            comp_tree_depth_sanity_limit)

    warn(":: => Done, building taxonomic search-space.",also_stdout=True)
    return per_comp_search_space