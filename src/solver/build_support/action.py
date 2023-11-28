import solver.build_support.arch as ar_
from saflib.saf.SkippingSAF import SkippingSAF
import copy
from collections import deque
from functools import cmp_to_key
from util.helper import info,warn,error

def compare_action_to_fmt_iface_bindings(A,B):
    '''
    Define preference structure for action-to-format-interface-bindings.\n\n

    Arguments:\n
    - A,B: {"target_fmt_iface":int,"target_rank_idx":int,
            "condition_fmt_iface":int,"condition_rank_idx":int}\n\n

    Returns: -1 if A<B, 0 if A==B, +1 is A>B
    '''
    def A_lt_B_case1(A,B):
        if A["target_fmt_iface"]==B["target_fmt_iface"] and \
           A["condition_fmt_iface"]==A["condition_fmt_iface"] and \
            ( \
                ( \
                    A["target_rank_idx"]<B["target_rank_idx"] and \
                    A["condition_rank_idx"]<=B["condition_rank_idx"] \
                ) or \
                ( \
                    A["target_rank_idx"]<=B["target_rank_idx"] and \
                    A["condition_rank_idx"]<B["condition_rank_idx"] \
                )
            ):
            return True
        return False
    def A_lt_B_case2(A,B):
        if ( \
                A["target_fmt_iface"]>B["target_fmt_iface"] and \
                A["condition_fmt_iface"]>=A["condition_fmt_iface"] \
        ) or \
        ( \
                A["target_fmt_iface"]>=B["target_fmt_iface"] and \
                A["condition_fmt_iface"]>A["condition_fmt_iface"] \
        ):
            return True
        return False
    
    # A<B: -1
    if A_lt_B_case1(A,B) or A_lt_B_case2(A,B):
        return -1
    # A>B: +1
    if A_lt_B_case1(B,A) or A_lt_B_case2(B,A):
        return +1
    # else: A==B
    return 0

def action_is_targeting_read_write_dataspace(target_dtype,user_attributes):
    '''
    True if an action's target dataspace is read-write (as opposed to read-only.)\n\n

    Arguments:\n
    - target_dtype -- action's target dataspace id \n
    - user_attributes -- user settings structure including read-write dataspace id, specified as follows:\n\n

    user_attributes=\n
    {\n
        dataspaces:\n
            read_write_dataspace_id: str dataspace id\n
    }
    '''
    read_write_dataspace=user_attributes['dataspaces']['read_write_dataspace_id']
    if target_dtype==read_write_dataspace:
        return True,read_write_dataspace
    return False,read_write_dataspace

def build_action_SAF_inference_problem_for_readonly_target(action_binding, \
                                                           fmt_iface_bindings):
    info("---- Building action SAF inference problem for read-only target.")
    target_buffer=action_binding['target']['buffer']
    target_dtype=action_binding['target']['dtype']
    condition_buffer=action_binding['condition']['buffer']
    condition_dtype=action_binding['condition']['dtype']
    target_fmt_ifaces=fmt_iface_bindings[target_buffer][target_dtype]
    condition_fmt_ifaces=fmt_iface_bindings[condition_buffer][condition_dtype]
    info("----- Target formats (buffer =",target_buffer,", dataspace =",target_dtype,")")
    info("------",target_fmt_ifaces)
    info("----- Condition formats (buffer =",condition_buffer,", datapsace =",condition_dtype,")")
    info("------",condition_fmt_ifaces)
    warn("---- => Done, building action SAF inference problem for read-only target.")
    return target_fmt_ifaces, condition_fmt_ifaces

def solve_action_SAF_inference_problem_for_readonly_target(target_fmt_ifaces, \
                                                           condition_fmt_ifaces):
    info("---- Solving action SAF inference problem for read-only target.")
    num_target_fmt_ifaces=len(target_fmt_ifaces)
    num_condition_fmt_ifaces=len(condition_fmt_ifaces)
    rank_to_sorted_target_fmt_iface_list={}
    rank_to_sorted_target_rank_idx_list={}
    rank_to_sorted_condition_fmt_iface_list={}
    rank_to_sorted_condition_rank_idx_list={}

    # Map fiber ranks to format interfaces
    info("----- Mapping fiber ranks to format interfaces")
    def flatten(lst):
        # Flatten nested lists into a single list.
        return [item for sublist in lst for item in \
                    (flatten(sublist) if isinstance(sublist, list) else [sublist])]
    for tdx,tfi in enumerate(target_fmt_ifaces):
        rank_list=flatten(tfi['fiber_layout'])
        for rdx,rank in enumerate(rank_list):
            rank_to_sorted_target_fmt_iface_list.setdefault(rank,deque([])).append(tdx)
            rank_to_sorted_target_rank_idx_list.setdefault(rank,deque([])).append(rdx)
    for cdx,cfi in enumerate(condition_fmt_ifaces):
        rank_list=flatten(cfi['fiber_layout'])
        for rdx,rank in enumerate(rank_list):
            rank_to_sorted_condition_fmt_iface_list.setdefault(rank,deque([])).append(cdx)
            rank_to_sorted_condition_rank_idx_list.setdefault(rank,deque([])).append(rdx)

    # Find common ranks between target, condition buffer/dataspace combos
    # (set intersection)
    common_ranks = rank_to_sorted_target_fmt_iface_list.keys() & \
                   rank_to_sorted_condition_fmt_iface_list.keys()
    
    info("------ Rank => sorted target fmt iface list:",rank_to_sorted_target_fmt_iface_list)
    info("------ Rank => sorted target rank idx list:",rank_to_sorted_target_rank_idx_list)
    info("------ Rank => sorted condition fmt iface list:",rank_to_sorted_condition_fmt_iface_list)
    info("------ Rank => sorted condition rank idx list:",rank_to_sorted_condition_rank_idx_list)
    info("------ Common target,condition ranks:",common_ranks)
    info("----- => Done, mapping fiber ranks to format interfaces")

    info("----- Building list of candidate action-to-format-interface bindings.")
    candidate_action_fmt_iface_bindings=deque([])
    for rank in common_ranks:
        target_fmt_iface_deque=rank_to_sorted_target_fmt_iface_list[rank]
        target_rank_idx_deque=rank_to_sorted_target_rank_idx_list[rank]
        condition_fmt_iface_deque=rank_to_sorted_condition_fmt_iface_list[rank]
        condition_rank_idx_deque=rank_to_sorted_condition_rank_idx_list[rank]
        while target_fmt_iface_deque and condition_fmt_iface_deque:
            candidate_action_fmt_iface_bindings.append({
                "target_fmt_iface":target_fmt_iface_deque.popleft(),
                "target_rank_idx":target_rank_idx_deque.popleft(),
                "condition_fmt_iface":condition_fmt_iface_deque.popleft(),
                "condition_rank_idx":condition_rank_idx_deque.popleft(),
                "rank":rank
            })
    info('------ Unsorted candidate list:',candidate_action_fmt_iface_bindings)

    # Sort s.t. more highly-preferred action-to-format-interface bindings come first
    sorted_candidate_action_fmt_iface_bindings = \
        sorted(candidate_action_fmt_iface_bindings, \
               key=cmp_to_key(compare_action_to_fmt_iface_bindings))
    info("------ Sorted candidate list:",sorted_candidate_action_fmt_iface_bindings)
    # Add action-to-format-interface bindings to final result list, discarding a binding if
    # on of its format interfaces is already bound
    valid_action_to_fmt_iface_bindings=deque([])
    discard_action_to_fmt_iface_bindings=deque([])
    visited_target_fmt_ifaces=[False for _ in list(range(num_target_fmt_ifaces))]
    visited_condition_fmt_ifaces=[False for _ in list(range(num_condition_fmt_ifaces))]
    for candidate in sorted_candidate_action_fmt_iface_bindings:
        target_fmt_iface=candidate["target_fmt_iface"]
        condition_fmt_iface=candidate["condition_fmt_iface"]
        if not (visited_target_fmt_ifaces[target_fmt_iface] or \
                visited_condition_fmt_ifaces[condition_fmt_iface]):
            valid_action_to_fmt_iface_bindings.append(candidate)
            visited_target_fmt_ifaces[target_fmt_iface]=True
            visited_condition_fmt_ifaces[condition_fmt_iface]=True
        else:
            discard_action_to_fmt_iface_bindings.append(candidate)
    info("------ Valid action-to-format-interface bindings:",valid_action_to_fmt_iface_bindings)
    info("------ Discarded action-to-format-interface bindings:",discard_action_to_fmt_iface_bindings)
    warn("----- => Done, building list of candidate action-to-format-interface bindings.")
    warn("---- => Done, solving action SAF inference problem for read-only target.")
    return list(valid_action_to_fmt_iface_bindings),list(discard_action_to_fmt_iface_bindings)

def print_skipping_SAF(target_buffer, \
                       target_fmt_iface_flat, \
                       condition_buffer, \
                       condition_fmt_iface_flat, \
                       bidirectional_setting):
    info("")
    info("skipping_saf = SkippingSAF.copy()")
    info(".target(",target_buffer,")")
    info(".set_attribute(\"bindings\",",str([target_buffer, \
                                             target_fmt_iface_flat, \
                                             condition_buffer, \
                                             condition_fmt_iface_flat]),")")
    info(".set_attribute(\"direction\",",bidirectional_setting,")")
    info("")

def build_skipping_SAFs(action_to_fmt_iface_bindings, \
                        original_action_to_buffer_dtype_binding, \
                        port_idx, \
                        saf_list=[]):
    def decode_is_bidirectional(is_bidirectional):
        if is_bidirectional:
            return "bidirectional"
        else:
            return "leader_follower"

    info("---- Building Skipping SAFs (",len(action_to_fmt_iface_bindings),")")
    target_buffer=original_action_to_buffer_dtype_binding['target']['buffer']
    target_dtype=original_action_to_buffer_dtype_binding['target']['dtype']
    condition_buffer=original_action_to_buffer_dtype_binding['condition']['buffer']
    condition_dtype=original_action_to_buffer_dtype_binding['condition']['dtype']
    bidirectional_setting=decode_is_bidirectional(original_action_to_buffer_dtype_binding['bidirectional'])
    info("----- Bidirectional setting =",bidirectional_setting)
    info("----- Target buffer =",target_buffer,", dataspace =",target_dtype)
    info("----- Condition buffer =",condition_buffer,", dataspace =",condition_dtype)
    for action_binding in action_to_fmt_iface_bindings:
        info("----- Building Skipping SAF for",action_binding)
        target_fmt_iface=action_binding['target_fmt_iface']
        condition_fmt_iface=action_binding['condition_fmt_iface']
        target_fmt_iface_flat=port_idx[target_buffer][target_dtype][target_fmt_iface]
        condition_fmt_iface_flat=port_idx[condition_buffer][condition_dtype][condition_fmt_iface]
        info("------ Flattening target format interface",str(target_fmt_iface), \
                                                        "to",str(target_fmt_iface_flat))
        info("------ Flattening condition format interface",str(condition_fmt_iface), \
                                                        "to",str(condition_fmt_iface_flat))
        info("------ SkippingSAF factory method calls:")
        print_skipping_SAF(target_buffer, \
                           target_fmt_iface_flat, \
                           condition_buffer, \
                           condition_fmt_iface_flat, \
                           bidirectional_setting)
        skipping_saf=SkippingSAF.copy() \
                                .target(target_buffer) \
                                .set_attribute("bindings",[target_buffer, \
                                                           target_fmt_iface_flat, \
                                                           condition_buffer, \
                                                           condition_fmt_iface_flat]) \
                                .set_attribute("direction",bidirectional_setting)
        saf_list.append(("skipping_saf",skipping_saf))
        warn("----- => Done, building Skipping SAF.")
    info("---- => Done, building Skipping SAFs")
    return saf_list

def build_action_SAFs(action_to_fmt_iface_bindings, \
                      action_type, \
                      original_action_to_buffer_dtype_binding, \
                      port_idx, \
                      saf_list=[]):
    if action_type=='skipping':
        saf_list=build_skipping_SAFs(action_to_fmt_iface_bindings, \
                                     original_action_to_buffer_dtype_binding, \
                                     port_idx,
                                     saf_list)
    elif action_type=='gating':
        error("Gating not yet supported.",also_stdout=True)
        info("Terminating.")
        assert(False)
    return saf_list

def get_action_SAFs_from_action_bindings(arch, \
                                         fmt_iface_bindings, \
                                         action_bindings, \
                                         dtype_list, \
                                         saf_list=[], \
                                         user_attributes={}):
    '''
    Generate action SAF (skip, gate) taxonomic representations from parsed action bindings.\n\n

    Each action binding may result in >=1 new action SAFs, depending on the number of format interface
    pairs which result from performing a join of the target and condition format interfaces.\n\n

    Arguments:\n
    - arch -- Sparseloop architecture YAML object\n
    - fmt_iface_bindings -- inferred bindings of rank representation format parsing interfaces to buffer stubs\n
        - Example:\n\n
        
        {'BackingStorage': \n
            {'Outputs': [], \n
             'Inputs': [{'format': 'UOP', 'fiber_layout': [['!0']]}, \n
                        ...\n
                        {'format': 'UOP', 'fiber_layout': [['R', 'E']]}\n
                       ],\n
             'Weights': ...},\n
         'iact_spad': ...,\n
         ...,\n
         'MAC': {'Outputs': [], 'Inputs': [], 'Weights': []}\n
        }\n\n

    - action_bindings -- inferred bindings of action SAFs to buffers\n
        - Example:\n\n

        [
            {'type': 'skipping', \n
             'bidirectional': False, \n
             'target': {'buffer': 'weight_spad', \n
                        'dtype': 'Weights'\n
                       }, 
             'condition': {'buffer': 'iact_spad', \n
                           'dtype': 'Inputs' \n
                          }, 
             'must_discard': False, \n
             'must_post_gate': False\n
            }\n
        ]\n\n
    - dtype_list -- inferred datatypes in the tensor problems addressable by this accelerator\n
        - Example: ['Weights', 'Outputs', 'Inputs']\n\n
    - saf_list -- taxonomic SAFs synthesized prior to this function call (list)
        
    Returns: saf_list with new action SAFs (if any) appended
    '''     

    info("-- Building action SAFs from action bindings.")
    info("--- architecture:",arch)
    info("--- format interface bindings:",str(fmt_iface_bindings))
    info("--- dataspaces:",dtype_list)

    port_idx = ar_.get_port_mappings_to_flattened_indices(arch, \
                                                          dtype_list, \
                                                          fmt_iface_bindings \
                                                         )
    info("--- Mapping from buffer/dataspace-dependent format interface ids to flattened ids:",port_idx)

    action_bindings=copy.deepcopy(action_bindings)
    for bdx in range(len(action_bindings)):
        action_binding=action_bindings[bdx]

        action_type=action_binding['type']
        info("--- Found \'",action_type,"\' action binding.")
        info("---- Binding:",action_binding)
        target_dtype=action_binding['target']['dtype']
        is_targeting_rw_dtype,read_write_dataspace = \
            action_is_targeting_read_write_dataspace(target_dtype,user_attributes)
        if is_targeting_rw_dtype:
            print(action_binding)
            error("Targeting read-write dataspaces with actions not yet supported.",also_stdout=True)
            info("Action:",action_binding)
            info("Terminating.")
            assert(False)
        else:
            info("---- Targets read-only dataspace.")
            target_fmt_ifaces, \
            condition_fmt_ifaces = \
                build_action_SAF_inference_problem_for_readonly_target(action_binding, \
                                                                       fmt_iface_bindings)
            action_to_fmt_iface_bindings,_ = \
                solve_action_SAF_inference_problem_for_readonly_target(target_fmt_ifaces, \
                                                                       condition_fmt_ifaces)
            saf_list = \
                build_action_SAFs(action_to_fmt_iface_bindings, \
                                  action_type, \
                                  action_binding, \
                                  port_idx, \
                                  saf_list)

        warn("--- => Done, building \'",action_type,"\' action.")

    warn("-- => Done, building action SAFs from action bindings.")
    return saf_list