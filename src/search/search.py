'''SAFsearch search functionality'''
from util.helper import info,warn,error,get_tqdm_outfile
from tqdm import tqdm
import search.search_support.life_cycle as lc_
from search.taxonomic.build.build_support.config_gen import build_user_attributes
from search.taxonomic.build.build_support.frontend import safinfer_frontend
from search.model.middle import safmodel_middle_layer
import copy

def safinfer_frontend_with_search_point(global_search_point, \
                                        arch,mapping,prob,sparseopts,reconfigurable_arch, \
                                        bind_out_path,saflib_path,safinfer_user_attributes,log_safinfer=False
                                       ):
    new_user_attributes=build_user_attributes(global_search_point, \
                                                  safinfer_user_attributes)
    return safinfer_frontend(arch,mapping,prob,sparseopts,reconfigurable_arch, \
                             bind_out_path,saflib_path,new_user_attributes,log_safinfer=log_safinfer)

def safmodel_middle_layer_get_objective(safinfer_results,arch,sparseopts,user_attributes,log_safmodel=False):
    taxo_uarch=safinfer_results['component_iterations'][-1]
    # test
    taxo_uarch.getId()

    abstract_analytical_primitive_models_dict, \
    abstract_analytical_component_models_dict, \
    scale_prob=safmodel_middle_layer(arch,taxo_uarch,sparseopts,user_attributes,log_safmodel=log_safmodel)
    objective=scale_prob["best_modeling_objective"]

    return objective, \
           {
               "abstract_analytical_primitive_models_dict":abstract_analytical_primitive_models_dict,
               "abstract_analytical_component_models_dict":abstract_analytical_component_models_dict,
               "scale_prob":scale_prob
           }

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
            safmodel_user_attributes, \
            characterization_path_list, \
            model_script_lib_list, \
            log_global_search_safinfer,
            log_global_search_safmodel):
    
    per_comp_search_space=global_search_space["per_comp_search_space"]
    top_lvl_comp_list=global_search_space["top_lvl_comp_list"]
    num_top_lvl_comps=global_search_space["num_top_lvl_comps"]
    per_comp_space_size_dict=global_search_space["per_comp_space_size_dict"]
    global_space_size=global_search_space["global_space_size"]

    # Results
    search_point_id_to_config_list=[]
    search_point_id_to_result_list=[]
    best_search_point_id=-1
    best_objective=float('inf')
    best_state=None
    best_global_search_point=None

    # Initialize search state
    search_point_id=0
    per_comp_search_state_dict={tlcomp:0 for tlcomp in top_lvl_comp_list}

    done=False
    for idx in tqdm(range(global_space_size), file=get_tqdm_outfile(), desc="Searching"):

        # Evaluate search point
        global_search_point=lc_.build_search_point(per_comp_search_state_dict, \
                                                   per_comp_search_space, \
                                                   top_lvl_comp_list)

        safinfer_results=safinfer_frontend_with_search_point(global_search_point, \
                                                             arch,mapping,prob,sparseopts,reconfigurable_arch, \
                                                             bind_out_path,saflib_path,safinfer_user_attributes, \
                                                             log_safinfer=log_global_search_safinfer
                                                            )

        objective, \
        _ = safmodel_middle_layer_get_objective(safinfer_results,arch,sparseopts,safmodel_user_attributes, \
                                           log_safmodel=log_global_search_safmodel)
        
        # Update best
        if objective < best_objective:
            best_objective=objective
            best_search_point_id=search_point_id
            best_state=copy.copy(per_comp_search_state_dict)
            best_global_search_point=copy.copy(global_search_point)
            warn("New best:",best_objective)
            info("- Objective:",best_objective,also_stdout=True)
            info("- Search-point:",best_search_point_id)

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
           best_objective, \
           best_state, \
           best_global_search_point