from util.sparse_bindings_reconfigurable import compute_reconfigurable_arch_bindings
import copy

def compute_read_only_action_binding(action, \
                                     option, \
                                     dtype_buffer_list, \
                                     target, \
                                     fmt_iface_bindings, \
                                     compute_optimization):
    if len(option['condition-on']) > 1:
        return None  # TODO: handle actions targeting read-only dataspaces with more than one condition
    condition_dtype = option['condition-on'][0] if option['condition-on'] else None
    # Find the next buffer that holds the condition datatype prior to the target buffer
    condition_buffer = None
    for buffer in dtype_buffer_list[condition_dtype]:
        if buffer == target['name']:
            if condition_buffer is None:
                condition_buffer = buffer
            break
        if condition_dtype in fmt_iface_bindings[buffer]:
            condition_buffer = buffer
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
                        action_binding=compute_read_only_action_binding(action, \
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