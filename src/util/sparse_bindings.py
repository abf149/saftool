import copy, numpy as np
from util.dense_bindings import *
from util.sparse_bindings_reconfigurable import compute_reconfigurable_arch_bindings

def compute_fixed_arch_bindings(arch,sparseopts):
    skip_bindings=[]
    dtype_list=extract_dtypes(sparseopts)
    fmt_iface_bindings,buff_dags,buffer_kept_dataspace_by_buffer = \
        bind_format_iface_to_fixed_arch(arch, sparseopts, dtype_list)
    dtype_buffer_list=transpose_bindings(fmt_iface_bindings)
    action_bindings=compute_action_bindings(sparseopts, fmt_iface_bindings, dtype_buffer_list)

    return fmt_iface_bindings, action_bindings, dtype_list, buff_dags, buffer_kept_dataspace_by_buffer

def extract_dtypes(sparseopts):
    targets = set()

    def recurse(node, in_dataspace=False, in_action_optimization=False):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'data-spaces':
                    recurse(value, in_dataspace=True, in_action_optimization=in_action_optimization)
                elif key == 'action-optimization':
                    recurse(value, in_dataspace=in_dataspace, in_action_optimization=True)
                elif key == 'name' and in_dataspace and isinstance(value, str):
                    targets.add(value)
                elif key == 'target' and in_action_optimization and isinstance(value, str):
                    targets.add(value)
                else:
                    recurse(value, in_dataspace=in_dataspace, in_action_optimization=in_action_optimization)
        elif isinstance(node, list):
            for item in node:
                recurse(item, in_dataspace=in_dataspace, in_action_optimization=in_action_optimization)

    recurse(sparseopts)
    return list(targets)

# Get buffer list for each datatype
def transpose_bindings(fmt_iface_bindings):
    transposed_bindings = {}

    for buffer, data in fmt_iface_bindings.items():
        for dtype in data.keys():
            if dtype not in transposed_bindings:
                transposed_bindings[dtype] = []
            transposed_bindings[dtype].append(buffer)

    return transposed_bindings

# sparseopts=copy.deepcopy(sparseopts['sparse_optimizations'])
def compute_action_bindings(sparseopts, fmt_iface_bindings, dtype_buffer_list):
    action_bindings = []
    compute_optimization = None

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
                    if len(option['condition-on']) > 1:
                        continue  # Skip if more than one condition
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
                    action_bindings.append({
                        'type': action['type'],
                        'bidirectional': False,
                        'target': {'buffer': target['name'], 'dtype': option['target']},
                        'condition': {'buffer': condition_buffer, 'dtype': condition_dtype},
                        'must_discard': must_discard,
                        'must_post_gate': must_post_gate
                    })

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

def compute_fmt_iface_bindings(buffer_dataspace_to_fmt_access_binding, dtype_list):
    dummy_rank_idx=0

    fmt_iface_bindings = {}

    for buffer, data in buffer_dataspace_to_fmt_access_binding.items():
        fmt_iface_bindings[buffer] = {}
        for dtype in dtype_list:
            fmt_iface_bindings[buffer][dtype] = []
            if 'representation-format' in data and dtype in data['representation-format']:
                for rank in data['representation-format'][dtype]['ranks']:

                    # Fiber rank(s)
                    fiber_layout = rank.get('flattened-rankIDs', [])
                    if len(fiber_layout) == 0:
                        # Create fictive rank fiber layout for fiber layouts
                        # not specified in sparseopts
                        fiber_layout.append(['!'+str(dummy_rank_idx)])
                        dummy_rank_idx += 1

                    fmt_iface_bindings[buffer][dtype].append({
                        'format': rank['format'],
                        'fiber_layout': fiber_layout
                    })

                    if 'metadata-word-bits' in rank:
                        fmt_iface_bindings[buffer][dtype][-1]['mdwidth']=rank['metadata-word-bits']

                    if 'payload-word-bits' in rank:
                        fmt_iface_bindings[buffer][dtype][-1]['payloadwidth']=rank['payload-word-bits']

    return fmt_iface_bindings

def get_buffer_dataspace_to_fmt_access_bindings_from_buffer_dataspace_to_fmt_layout_bindings_fixed_arch(buffer_dataspace_to_fmt_layout_binding, flat_arch, dtype_list):
    '''
    Sparseloop's sparseopts spec binds a fiber to a datatype and buffer-level.
    A sparseopts binding or memory level will reside in that memory level,
    but the buffer's address generaters will only *traverse* a subset of fibers
    at that buffer-level. Untraversed fibers residing at some buffer level
    comprise a tile which will be filled into lower memory where it will be traversed.

    This function consumes sparseopts-style fiber bindings and re-binds fibers 
    to the memory levels where they are traversed.
    '''
    
    buffer_dataspace_to_fmt_access_binding=copy.deepcopy(buffer_dataspace_to_fmt_layout_binding)

    top_lvl_buffer=list(flat_arch.keys())[0]
    last_resident_buffer={dtype:top_lvl_buffer for dtype in dtype_list}

    idx_to_buffer=[buffer for buffer in flat_arch]
    idx_to_buffer.append("sentinel")    
    num_arch_lvls=len(idx_to_buffer)
    buff_used_by_dtype={dtype:(([False]*(num_arch_lvls-1))+[True]) for dtype in dtype_list}
    buffer_to_idx={buffer:idx_to_buffer.index(buffer) for buffer in idx_to_buffer}

    buff_dags={dtype: [[False for _ in idx_to_buffer] for _ in idx_to_buffer] \
                       for dtype in dtype_list}

    buffer_kept_dataspace_by_buffer={buffer:list(buffer_dataspace_to_fmt_layout_binding[buffer] \
                                                                                      ['representation-format'] \
                                                                                      .keys()) \
                                        for buffer in flat_arch}

    # Re-bind fibers to the buffer levels at which they are accessed
    for bdx,buffer in enumerate(flat_arch):
        buffer_kept_data_spaces = \
            buffer_kept_dataspace_by_buffer[buffer]
        for dtype in dtype_list:
            if dtype in buffer_kept_data_spaces:
                # For each datatype resident in this buffer level,
                upper_buffer=last_resident_buffer[dtype]
                if upper_buffer != buffer:

                    buff_dags[dtype] \
                             [buffer_to_idx[upper_buffer]][bdx]=True

                    buff_used_by_dtype[dtype][buffer_to_idx[upper_buffer]]=True

                    #if this buffer level is **not** top-level memory,
                    if dtype in buffer_dataspace_to_fmt_layout_binding[upper_buffer]['representation-format']:
                        # and if there are any sparse fibers at this buffer level for this datatype,
                        # then omit this tile from the lowest higher buffer level which keeps this datatype
                        buffer_dtype_tile=buffer_dataspace_to_fmt_layout_binding[buffer]['representation-format'][dtype]['ranks']                        
                        upper_buffer_dtype_tile=copy.deepcopy(buffer_dataspace_to_fmt_layout_binding[upper_buffer]['representation-format'][dtype]['ranks'])
                        
                        
                        buffer_data_storage_depth=flat_arch[buffer]['attributes']['data_storage_depth']
                        buffer_data_storage_width=flat_arch[buffer]['attributes']['data_storage_width']
                        buffer_datawidth=flat_arch[buffer]['attributes']['datawidth']
                        if buffer_data_storage_width==buffer_datawidth and buffer_data_storage_depth==1:
                            # If buffer holds only a singleton data word, do not 
                            # suffix-prune upper_buffer
                            assert(len(buffer_dtype_tile)==1) # For now - singleton registers must be singleton rank
                            fiber_layout=[]
                            buffer_singleton_rank=buffer_dtype_tile[0]
                            upper_buffer_singleton_rank=upper_buffer_dtype_tile[-1]
                            if 'flattened-rankIDs' in upper_buffer_singleton_rank:
                                fiber_layout=upper_buffer_singleton_rank['flattened-rankIDs']
                                buffer_dataspace_to_fmt_access_binding \
                                    [buffer]['representation-format'][dtype]['ranks'][-1]['flattened-rankIDs']=fiber_layout                              
                            elif 'flattened-rankIDs' in buffer_singleton_rank:
                                fiber_layout=buffer_singleton_rank['flattened-rankIDs']
                                upper_buffer_dtype_tile[-1]['flattened-rankIDs']=fiber_layout                                    

                            buffer_dataspace_to_fmt_access_binding[upper_buffer]['representation-format'][dtype]['ranks'] = \
                                upper_buffer_dtype_tile
                        else:
                            # Otherwise, suffix-prune the fiber subtree at upper_buffer, 
                            # TODO: more efficient approach to suffix pruning
                            num_buffer_dtype_tile_fibers=len(buffer_dtype_tile)
                            num_upper_buffer_dtype_tile_fibers=len(upper_buffer_dtype_tile)
                            num_traversed_upper_buffer_dtype_tile_fibers= \
                                num_upper_buffer_dtype_tile_fibers-num_buffer_dtype_tile_fibers
                            traversed_upper_buffer_dtype_tile_fibers= \
                                upper_buffer_dtype_tile[0:num_traversed_upper_buffer_dtype_tile_fibers]

                            buffer_dataspace_to_fmt_access_binding[upper_buffer]['representation-format'][dtype]['ranks']= \
                                traversed_upper_buffer_dtype_tile_fibers

                last_resident_buffer[dtype]=buffer

    for dtype in dtype_list:     
        for idx in range(num_arch_lvls-1):
            if (not buff_used_by_dtype[dtype][idx]) and \
               (dtype in buffer_kept_dataspace_by_buffer[idx_to_buffer[idx]]):

                buff_dags[dtype][idx][num_arch_lvls-1]=True

    return buffer_dataspace_to_fmt_access_binding, buff_dags, buffer_kept_dataspace_by_buffer

def bind_format_iface_to_fixed_arch(arch, sparseopts, dtype_list):
    '''Bind format interfaces to buffers, loops, ranks, formats & address arithmetic'''

    # Extract data-space, mapping & flattened architecture info
    flat_arch=flatten_arch_wrapper(arch)
    buffer_dataspace_to_fmt_layout_binding=get_buffer_dataspace_to_fmt_layout_bindings_from_sparseopts(sparseopts)
    

    buffer_dataspace_to_fmt_access_binding, buff_dags, buffer_kept_dataspace_by_buffer = \
        get_buffer_dataspace_to_fmt_access_bindings_from_buffer_dataspace_to_fmt_layout_bindings_fixed_arch \
            (buffer_dataspace_to_fmt_layout_binding, flat_arch, dtype_list)

    fmt_ifaces = compute_fmt_iface_bindings( \
        copy.deepcopy(buffer_dataspace_to_fmt_access_binding), \
            dtype_list)

    return fmt_ifaces, buff_dags, buffer_kept_dataspace_by_buffer

