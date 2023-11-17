'''SAFsearch search functionality'''
from util.helper import info,warn,error
from tqdm import tqdm
import search.search_support.life_cycle as lc_

def search(global_search_space, \
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
            characterization_path_list, \
            model_script_lib_list, \
            log_taxo_component_search_space_discovery):
    
    per_comp_search_space=global_search_space["per_comp_search_space"]
    top_lvl_comp_list=global_search_space["top_lvl_comp_list"]
    num_top_lvl_comps=global_search_space["num_top_lvl_comps"]
    per_comp_space_size_dict=global_search_space["per_comp_space_size_dict"]
    global_space_size=global_search_space["global_space_size"]

    # Results
    search_point_id_to_config_list=[]
    search_point_id_to_result_list=[]
    best_search_point_id=-1
    best_objective=-1.0

    # Initialize search state
    search_point_id=0
    per_comp_search_state_dict={tlcomp:0 for tlcomp in top_lvl_comp_list}

    done=False
    for idx in tqdm(range(global_space_size), desc="Searching"):
        objective=-1.0

        # Evaluate search point


        # Update results
        lc_.update_results(objective, \
                           search_point_id, \
                           per_comp_search_state_dict, \
                           search_point_id_to_config_list, \
                           search_point_id_to_result_list)

        # Next state
        search_point_id, \
        per_comp_search_state_dict, \
        done=lc_.step_state(search_point_id, \
                            per_comp_search_state_dict, \
                            per_comp_space_size_dict, \
                            top_lvl_comp_list, \
                            num_top_lvl_comps)
    
    # Assert that final state was reached
    lc_.assert_done(done, \
                    search_point_id, \
                    per_comp_search_state_dict, \
                    per_comp_space_size_dict, \
                    top_lvl_comp_list, \
                    num_top_lvl_comps, \
                    global_space_size)

    return search_point_id_to_config_list, \
           search_point_id_to_result_list, \
           best_search_point_id, \
           best_objective