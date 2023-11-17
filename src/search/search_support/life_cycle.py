'''Routines for managing the life-cycle of the SAFsearch search process'''
from util.helper import info,warn,error
import copy

def assert_done(done, \
                search_point_id, \
                per_comp_search_state_dict, \
                per_comp_space_size_dict, \
                top_lvl_comp_list, \
                num_top_lvl_comps, \
                global_space_size):
    if not done:
            error("Global search space of size",global_space_size,"but states remain unexplored.",also_stdout=True)
            info("- Search-point:",search_point_id)
            info("- State:",per_comp_search_state_dict)
            info("- Per-comp search-space sizes:",per_comp_space_size_dict)
            info("- Number of top-level component search-spaces:",num_top_lvl_comps)
            info("Terminating.")
            assert(False)

def step_state(search_point_id, \
               per_comp_search_state_dict, \
               per_comp_space_size_dict, \
               top_lvl_comp_list, \
               num_top_lvl_comps):
    '''
    Generate next search point and associated search state.\n
    - search_point_id => search_point_id+1
    - per_comp_search_state_dict is updated in an addition-with-carry fashion:
        - Base-case: step_state() will start by updating top_lvl_comp_list[0] state
        - Inductive case, for top-level component state space n < num_top_lvl_comps:
            - tlcomp_n = top_lvl_comp_list[n]
            - tlcomp_{n+1} = top_lvl_comp_list[n+1]
            - if per_comp_search_state_dict


    Returns:\n
    - search_point_id+1\n
    - New search state dict
    - Done (bool); True if full search-space has been explored

    '''
    for cdx,tlcomp in enumerate(top_lvl_comp_list):
        tlcomp_state=per_comp_search_state_dict[tlcomp]
        tlcomp_max=per_comp_space_size_dict[tlcomp]-1
        if tlcomp_state > tlcomp_max:
            error("Invalid search state for top-level component",tlcomp, \
                  ": state value",str(tlcomp_state),"exceeds max",str(tlcomp_max),also_stdout=True)
            info("State: search_point",search_point_id,", state",str(per_comp_search_state_dict))
            info("Terminating.")
            assert(False)
        if tlcomp_state == tlcomp_max:
            per_comp_search_state_dict[tlcomp] = 0
            if cdx==num_top_lvl_comps-1:
                return None, \
                       None, \
                       True
        else:
            per_comp_search_state_dict[tlcomp] = per_comp_search_state_dict[tlcomp]+1
            return search_point_id+1, \
                   per_comp_search_state_dict, \
                   False

def update_results(objective, \
                   search_point_id, \
                   per_comp_search_state_dict, \
                   search_point_id_to_config_list, \
                   search_point_id_to_result_list):

    res_dict = { \
                    "objective":objective,
                    "search_point_id":search_point_id,
                    "search_state":copy.copy(per_comp_search_state_dict)
               }
    search_point_id_to_config_list.append(copy.copy(per_comp_search_state_dict))
    search_point_id_to_result_list.append(res_dict)
    assert search_point_id == len(search_point_id_to_config_list)-1
    assert search_point_id == len(search_point_id_to_result_list)-1