from util import sparseloop_config_processor as sl_config, safinfer_io, safmodel_io
from solver.solve import Solver
from solver.build import build_taxonomic_arch_and_safs_from_bindings
from util.helper import info,warn,error
import util.helper as helper
import util.safsearch_io as safsearch_io
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

def get_sparse_matches_dict(attribute_vals,matches_list,attributes):
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

def synthesize_user_settings_syntax(sparse_match_spec):
    res={'type':'positional'}
    sparse_match_template=sparse_match_spec['sparse_match_template']
    sparse_match_id=sparse_match_spec['sparse_match_id']
    sparse_match=sparse_match_spec['sparse_match']
    # Note: the 'name' field is not used by SAFinfer and is
    # more of a comment intended for a user who is debugging.
    res['values'] = [ \
            {'position':sparse_match_template[idx]['idx'], \
             'name':sparse_match_template[idx]['name'], \
             'value':value} \
                for idx,value in enumerate(sparse_match)
    ]
    return {'uri':sparse_match_spec['uri'],'settings':[res]}

def build_user_attributes(component_attribute_configs_list,safinfer_user_attributes):
    new_user_attributes=copy.copy(safinfer_user_attributes)
    force_attributes_list=[]
    for sparse_match_spec in component_attribute_configs_list:
        # Synthesize "user" settings which force the attribute values
        # associated with the current search-point
        force_attributes_list.append(synthesize_user_settings_syntax(sparse_match_spec))
    if len(force_attributes_list)>0:
        # Insert attribute forcing settings into user attributes structure,
        # unless there are no attribute forcing settings
        if 'force_attributes' in new_user_attributes \
            and (new_user_attributes['force_attributes'] is not None):

            new_user_attributes['force_attributes'].extend(force_attributes_list)
        else:
            new_user_attributes['force_attributes'] = force_attributes_list
        return new_user_attributes
    if 'stdout' not in safinfer_user_attributes or safinfer_user_attributes['stdout']:
        # Silence SAFinfer standard output logging.
        new_user_attributes['stdout']=False
        return new_user_attributes
    return safinfer_user_attributes

def assert_comp_tree_depth_sanity(tree_depth,comp_tree_depth_sanity_limit,final_configs_dict):
    if tree_depth > comp_tree_depth_sanity_limit:
        error("While building taxo search space, search-tree depth", \
              str(tree_depth),"exceeded",str(comp_tree_depth_sanity_limit))
        print_search_space(final_configs_dict,incomplete=True)
        info("Terminating.")
        assert(False)

def disable_logs(disable_file_log=False):
    stream_state = {
        'stdout':helper.enable_stdout,
        'stderr':helper.enable_stderr,
        'log':helper.enable_log,
    }
    safsearch_io.disable_stdout()
    safsearch_io.disable_stderr()
    if disable_file_log:
        safsearch_io.log_control(False)
    return stream_state

def revert_logs(stream_state):
    if stream_state['stdout']:
        safsearch_io.enable_stdout()
    else:
        safsearch_io.disable_stdout()
    if stream_state['stderr']:
        safsearch_io.enable_stderr()
    else:
        safsearch_io.disable_stderr()
    safsearch_io.log_control(stream_state['log'])

def build_component_search_space(arch, \
                                 safinfer_user_attributes, \
                                 mapping, \
                                 prob, \
                                 sparseopts, \
                                 reconfigurable_arch, \
                                 bind_out_path, \
                                 saflib_path, \
                                 last_uri="", \
                                 component_attribute_configs_list=[], \
                                 final_configs_dict={}, \
                                 comp_attr_spec_dict={}, \
                                 tree_depth=0, \
                                 comp_tree_depth_sanity_limit=100):
    
    # TODO: APPLY CONFIGS
    new_user_attributes=build_user_attributes(component_attribute_configs_list,safinfer_user_attributes)
    warn('SAFsearch applying SAFinfer user_attributes:',new_user_attributes)

    stream_state=disable_logs()
    result = safinfer.pipeline(arch,mapping,prob,sparseopts,reconfigurable_arch, \
                               bind_out_path,saflib_path,user_attributes=new_user_attributes)
    revert_logs(stream_state)

    outcome,uri,attribute_vals,supported_instances,attributes = \
        extract_key_results(result)

    top_lvl_comp_w_failure=None
    if not outcome:
        # Upon taxonomic inference failure, determine top-level taxonomic component
        # which is the root of the tree that contains the failing component
        top_lvl_comp_w_failure=get_uri_top_component(uri)
        comp_attr_spec_dict[uri]=attributes
    if outcome or (last_uri != "" and top_lvl_comp_w_failure != get_uri_top_component(last_uri)):
        #assert(False)
        # Termination condition - complete success, or single component is fully recursively solved;
        # save config
        if not outcome:
            # Single component recursively solved, but overall architecture is unsolved
            if top_lvl_comp_w_failure not in final_configs_dict:
                final_configs_dict[top_lvl_comp_w_failure]=[copy.copy(component_attribute_configs_list)]
            else:
                final_configs_dict[top_lvl_comp_w_failure].append(copy.copy(component_attribute_configs_list))
        else:
            # Overall architecture is solved
            last_top_lvl_comp_w_failure = get_uri_top_component(last_uri)
            if last_top_lvl_comp_w_failure not in final_configs_dict:
                final_configs_dict[last_top_lvl_comp_w_failure]=[copy.copy(component_attribute_configs_list)]
            else:
                final_configs_dict[last_top_lvl_comp_w_failure].append(copy.copy(component_attribute_configs_list))
        return outcome

    # Failure, and current top-level component is not yet fully recursively-solved;
    # recurse to next component or subcomponent

    matches_list=findAllInstancesPartiallyMatchingObjectAttributes \
                    (attribute_vals,supported_instances,attributes)
    sparse_matches_dict, sparse_match_template=get_sparse_matches_dict(attribute_vals,matches_list,attributes)
    all_complete=True
    for sparse_match_id in sparse_matches_dict:
        new_component_attribute_configs_list=copy.copy(component_attribute_configs_list)
        new_component_attribute_configs_list.append({"uri":uri, \
                                                     "sparse_match_template":sparse_match_template, \
                                                     "sparse_match_id":sparse_match_id, \
                                                     "sparse_match":sparse_matches_dict[sparse_match_id]})
        
        all_complete = all_complete and \
            build_component_search_space(arch, \
                                         safinfer_user_attributes, \
                                         mapping, \
                                         prob, \
                                         sparseopts, \
                                         reconfigurable_arch, \
                                         bind_out_path, \
                                         saflib_path, \
                                         last_uri=uri, \
                                         component_attribute_configs_list=new_component_attribute_configs_list, \
                                         final_configs_dict=final_configs_dict, \
                                         tree_depth=tree_depth+1, \
                                         comp_tree_depth_sanity_limit=comp_tree_depth_sanity_limit)

    return all_complete

def assert_top_lvl_comp_cnt_sanity(top_lvl_comp_cnt,top_lvl_comp_cnt_sanity_limit,final_configs_dict):
    if top_lvl_comp_cnt > top_lvl_comp_cnt_sanity_limit:
        error("While building taxo search space, failing top-level component count", \
              str(top_lvl_comp_cnt),"exceeded sanity limit of",str(top_lvl_comp_cnt_sanity_limit))
        print_search_space(final_configs_dict,incomplete=True)
        info("Terminating.")
        assert(False)

def print_search_space(final_configs_dict,incomplete=False):
    num_components=len(final_configs_dict)
    if not incomplete:
        warn("SAFsearch discovered taxonomic search spaces for",str(num_components),"top-level component(s)",also_stdout=True)
        info("Search space summary:")
    else:
        info("Incomplete search space:")
    for comp_uri in final_configs_dict:
        comp_search_space=final_configs_dict[comp_uri]
        num_search_points=len(comp_search_space)
        info("- Search tree rooted at",comp_uri,"(",str(num_search_points),"search-points):")
        for idx,search_point in enumerate(comp_search_space):
            num_settings=len(search_point)
            info("-- Search-point",str(idx),"config (",str(num_settings),")")
            for setting in search_point:
                comp_uri=setting['uri']
                sparse_match_template=setting['sparse_match_template']
                sparse_match_id=setting['sparse_match_id']
                sparse_match=setting['sparse_match']
                info("---",comp_uri,"(",sparse_match_id,"):")
                for sdx,attr_val in enumerate(sparse_match):
                    attr_info=sparse_match_template[sdx]
                    info("----",attr_info['name'],"(attr. idx =",str(attr_info['idx']),"):",attr_val)

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
    
    info(":: Building taxonomic component search space...",also_stdout=True)

    final_configs_dict={}
    top_lvl_comp_cnt=0
    comp_attr_spec_dict={}
    info("Beginning build process...")
    info("- top_lvl_comp_cnt_sanity_limit =",top_lvl_comp_cnt_sanity_limit)
    info("- comp_tree_depth_sanity_limit =",comp_tree_depth_sanity_limit)
    while not build_component_search_space(arch, \
                                           safinfer_user_attributes, \
                                           mapping, \
                                           prob, \
                                           sparseopts, \
                                           reconfigurable_arch, \
                                           bind_out_path, \
                                           saflib_path, \
                                           last_uri="", \
                                           component_attribute_configs_list=[], \
                                           final_configs_dict=final_configs_dict, \
                                           comp_attr_spec_dict=comp_attr_spec_dict, \
                                           comp_tree_depth_sanity_limit=comp_tree_depth_sanity_limit):
        # Each iteration builds the search space for a different top-level component
        top_lvl_comp_cnt+=1
        assert_top_lvl_comp_cnt_sanity(top_lvl_comp_cnt,top_lvl_comp_cnt_sanity_limit,final_configs_dict)
    warn("=> Done, build process.")
    info("\n\n")
    print_search_space(final_configs_dict,incomplete=False)

    warn(":: => Done, building taxonomic component search space",also_stdout=True)
    return final_configs_dict