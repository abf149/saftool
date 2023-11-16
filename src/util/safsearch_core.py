from util import sparseloop_config_processor as sl_config, safinfer_io, safmodel_io
from solver.solve import Solver
from solver.build import build_taxonomic_arch_and_safs_from_bindings
from util.helper import info,warn,error
from util.notation.generators.rules import findAllInstancesPartiallyMatchingObjectAttributes
import util.notation.predicates as pr_
import saflib.microarchitecture.TaxoRegistry as tr_ # Initialize taxonomic registry (TODO: from files)
#from util.safinfer_io import sprettyprint_taxo_uarch
#from solver.build import get_buffer_hierarchy
import solver.model.build as build
import solver.model.solve as solve
import safinfer
import copy
#import util.helper as helper

def extract_key_results(result):
    outcome=result['outcome']
    uri=result['uri']
    failure_comp=result['failure_comp']
    if not outcome:
        id_=failure_comp.getId()
        attribute_vals=failure_comp.getAttributes()
        attributes=None
        category=failure_comp.getCategory()
        supported_instances={}
        description=None
        if pr_.isPrimitive(failure_comp):
            primitive_info=tr_.getPrimitive(category)
            supported_instances=primitive_info['instances']
            description=primitive_info['description']
        elif pr_.isComponent(failure_comp):
            component_info=tr_.getComponent(category)
            supported_instances=component_info['instances']
            description=component_info['description']
        else:
            error("Component",id_,"(category",category,") is neither primitive nor component.")
            info("Terminating.")
            assert(False)
        attributes=description.get_attributes()
        return outcome,uri,attribute_vals,supported_instances,attributes
    else:
        return True,None,None,None,None

def get_sparse_matches_list(attribute_vals,matches_list,attributes):
    attr_names=[attr_spec[0] for attr_spec in attributes]
    sparse_match_template=[]
    sparse_matches_dict={}
    for idx,val in enumerate(attribute_vals):
        if val=="?":
            sparse_match_template.append({"idx":idx,"name":attr_names[idx]})
    for match in matches_list:
        sparse_matches_dict[match['inst_name']] = \
            tuple([match['inst_attr'][sparse_match_attr["idx"]] \
                   for sparse_match_attr in sparse_match_template])
    return sparse_matches_dict, sparse_match_template

def get_uri_top_component(uri):
    uri_split=uri.split('.')
    assert(len(uri_split)>1)
    return uri_split[1]

def safinfer_trial(arch, \
                   mapping, \
                   prob, \
                   sparseopts, \
                   reconfigurable_arch, \
                   bind_out_path, \
                   saflib_path, \
                   last_uri="", \
                   component_attribute_configs_list=[], \
                   final_configs_dict={}):
    
    # TODO: APPLY CONFIGS

    result = safinfer.pipeline(arch,mapping,prob,sparseopts,reconfigurable_arch, \
                               bind_out_path,saflib_path)
    outcome,uri,attribute_vals,supported_instances,attributes = \
        extract_key_results(result)

    top_lvl_comp_w_failure=get_uri_top_component(uri)
    print(top_lvl_comp_w_failure)
    if outcome or (last_uri != "" and top_lvl_comp_w_failure != get_uri_top_component(last_uri)):
        assert(False)
        # Termination condition - complete success, or single component is fully recursively solved;
        # save config
        if top_lvl_comp_w_failure not in final_configs_dict:
            final_configs_dict[top_lvl_comp_w_failure]=[copy.copy(component_attribute_configs_list)]
        else:
            final_configs_dict[top_lvl_comp_w_failure].append(copy.copy(component_attribute_configs_list))
        return outcome

    # Failure, and current top-level component is not yet fully recursively-solved;
    # recurse to next component or subcomponent

    matches_list=findAllInstancesPartiallyMatchingObjectAttributes \
                    (attribute_vals,supported_instances,attributes)
    sparse_matches_list, sparse_match_template=get_sparse_matches_list(attribute_vals,matches_list,attributes)
    #print(sparse_matches_list)
    #print(sparse_match_template)
    all_complete=True
    for sparse_match in sparse_matches_list:
        new_component_attribute_configs_list=copy.copy(component_attribute_configs_list)
        new_component_attribute_configs_list.append({"uri":uri, \
                                                     "sparse_match_template":sparse_match_template, \
                                                     "sparse_matches_list":sparse_matches_list})
        
        print(new_component_attribute_configs_list)
        print(uri)
        print(final_configs_dict)
        
        assert(False)

        all_complete = all_complete and \
            safinfer_trial(arch, \
                           mapping, \
                           prob, \
                           sparseopts, \
                           reconfigurable_arch, \
                           bind_out_path, \
                           saflib_path, \
                           last_uri=uri, \
                           component_attribute_configs_list=new_component_attribute_configs_list, \
                           final_configs_dict=final_configs_dict)

    return all_complete

def search_loop(arch, \
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
    model_script_lib_list):
    
    final_configs_dict={}

    while not safinfer_trial(arch, \
                             mapping, \
                             prob, \
                             sparseopts, \
                             reconfigurable_arch, \
                             bind_out_path, \
                             saflib_path, \
                             last_uri="", \
                             component_attribute_configs_list=[], \
                             final_configs_dict=final_configs_dict):
        pass

    return