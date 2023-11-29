from util.sparse_bindings_reconfigurable import compute_reconfigurable_arch_bindings
import util.bind_support.format as fmt_
from util.helper import info,warn,error
import copy

def find_condition_buffer(condition_dtype,dtype_buffer_list,target,fmt_iface_bindings):
    condition_buffer = None
    idx = None
    for jdx,buffer in enumerate(dtype_buffer_list[condition_dtype]):
        if buffer == target['name']:
            if condition_buffer is None:
                condition_buffer = buffer
                idx = jdx
            break
        if fmt_.buffer_keeps_dtype(condition_dtype,buffer,fmt_iface_bindings):
            condition_buffer = buffer
            idx = jdx

    return condition_buffer,idx

def compute_read_only_action_binding(action, \
                                     option, \
                                     dtype_buffer_list, \
                                     target, \
                                     fmt_iface_bindings, \
                                     compute_optimization):

    if len(option['condition-on']) > 1:
        return None  # TODO: handle actions targeting read-only dataspaces with more than one condition
    condition_dtype = option['condition-on'][0] if option['condition-on'] else None
    condition_buffer,_ = find_condition_buffer(condition_dtype,dtype_buffer_list,target,fmt_iface_bindings)
    must_discard = compute_optimization == 'skipping' and condition_buffer == dtype_buffer_list[condition_dtype][-1]
    must_post_gate = compute_optimization == 'gating' and condition_buffer == dtype_buffer_list[condition_dtype][-1]

    return {
            'type': action['type'],
            'bidirectional': False,
            'target': {'buffer': target['name'], 'dtype': option['target']},
            'condition': {'buffer': condition_buffer, 'dtype': condition_dtype},
            'must_discard': must_discard,
            'must_post_gate': must_post_gate
           }

def compute_read_write_action_binding(action, \
                                     option, \
                                     dtype_buffer_list, \
                                     target, \
                                     fmt_iface_bindings, \
                                     compute_optimization):
    #if len(option['condition-on']) > 1:
    #    return None  # TODO: handle actions targeting read-only dataspaces with more than one condition
    note={
            "action":action,
            "option":option,
            "dtype_buffer_list":dtype_buffer_list,
            "target":target,
            "fmt_iface_bindings":fmt_iface_bindings,
            "compute_optimization":compute_optimization
         }
    condition_dtype_list = option['condition-on'] if option['condition-on'] else None
    condition_buffer_list = []
    bdx_list = []

    if condition_dtype_list is None:
        error("None-valued condition_dtype_list not currently supported.",also_stdout=True)
        info("- action:",action)
        info("- option:",option)
        info("- dtype_buffer_list:",dtype_buffer_list)
        info("- target:",target)
        info("- fmt_iface_bindings:",fmt_iface_bindings)
        info("- compute_optimization:",compute_optimization)
        info("Terminating.")
        assert(False)
    # Find the next buffer that holds the condition datatype prior to the target buffer

    #best_condition_dtype=None
    #best_condition_buffer=None
    #best_bdx=None

    for condition_dtype in condition_dtype_list:
        condition_buffer, \
        bdx = find_condition_buffer(condition_dtype, \
                                    dtype_buffer_list, \
                                    target, \
                                    fmt_iface_bindings)
        
        condition_buffer_list.append(condition_buffer)
        bdx_list.append(bdx)
        #if (condition_buffer is not None) and (best_condition_buffer is None or bdx > best_bdx):
        #    best_condition_dtype=condition_dtype
        #    best_condition_buffer=condition_buffer
        #    best_bdx=bdx

    #if best_condition_buffer is None:
    #    error("Failed to find condition buffer for action targeting read-write dataspace.",also_stdout=True)
    #    info("- action:",action)
    #    info("- option:",option)
    #    info("- dtype_buffer_list:",dtype_buffer_list)
    #    info("- target:",target)
    #    info("- fmt_iface_bindings:",fmt_iface_bindings)
    #    info("- compute_optimization:",compute_optimization)
    #    info("Terminating.")
    #    assert(False)
    
    #must_discard = compute_optimization == 'skipping' and best_condition_buffer == dtype_buffer_list[best_condition_dtype][-1]
    #must_post_gate = compute_optimization == 'gating' and best_condition_buffer == dtype_buffer_list[best_condition_dtype][-1]

    # Step 1: Sort bdx_list in decreasing order and get the permutation associated with the sort
    reverse_sort_w_permutation=sorted(enumerate(bdx_list), key=lambda x: x[1], reverse=True)
    permutation=[tup[0] for tup in reverse_sort_w_permutation]
    sorted_bdx_list=[tup[1] for tup in reverse_sort_w_permutation]

    # Step 2: Permute the other two lists to match the sorting permutation applied to bdx_list
    condition_dtype_list = [condition_dtype_list[i] for i in permutation]
    condition_buffer_list = [condition_buffer_list[i] for i in permutation]

    must_discard = False
    must_post_gate = False

    return {
            'type': action['type'],
            'bidirectional': False,
            'target': {'buffer': target['name'], 'dtype': option['target']},
            'condition': {'buffer': condition_buffer_list[0], 'dtype': condition_dtype_list[0]},
            'condition_list': {'buffer_list': condition_buffer_list, 'dtype_list': condition_dtype_list},
            'must_discard': must_discard,
            'must_post_gate': must_post_gate,
            'note':note
           }

def compute_action_bindings(sparseopts, fmt_iface_bindings, dtype_buffer_list, user_attributes):
    action_bindings = []
    compute_optimization = None
    read_write_dataspace=user_attributes['dataspaces']['read_write_dataspace_id']

    sparseopts=copy.deepcopy(sparseopts['sparse_optimizations'])

    # First, find compute optimization
    for target in sparseopts['targets']:
        if 'compute-optimization' in target:
            compute_optimization = target['compute-optimization'][0]['type']

    # Then, process action optimizations
    for target in sparseopts['targets']:
        if 'action-optimization' in target:
            for action in target['action-optimization']:
                for option in action['options']:
                    if read_write_dataspace != option['target']:
                        action_binding=compute_read_only_action_binding(action, \
                                                                        option, \
                                                                        dtype_buffer_list, \
                                                                        target, \
                                                                        fmt_iface_bindings, \
                                                                        compute_optimization)
                        if action_binding is not None:
                            action_bindings.append(action_binding)
                    else:
                        action_binding=compute_read_write_action_binding(action, \
                                                                         option, \
                                                                         dtype_buffer_list, \
                                                                         target, \
                                                                         fmt_iface_bindings, \
                                                                         compute_optimization)

                        if action_binding is not None:
                            action_bindings.append(action_binding)

    # Finally, check for bidirectional actions
    bidirectional_actions = []
    for i in range(len(action_bindings)):
        for j in range(i+1, len(action_bindings)):
            if action_bindings[i]['target'] == action_bindings[j]['condition'] and action_bindings[i]['condition'] == action_bindings[j]['target'] and action_bindings[i]['type'] == action_bindings[j]['type']:
                action_bindings[i]['bidirectional'] = True
                bidirectional_actions.append(action_bindings[i])

    # Filter out the unidirectional counterparts of bidirectional actions
    action_bindings = [action for action in action_bindings if not (action['bidirectional'] and action not in bidirectional_actions)]

    return action_bindings