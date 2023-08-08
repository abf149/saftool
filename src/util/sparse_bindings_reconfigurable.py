import copy
from util.dense_bindings import *

def compute_reconfigurable_arch_bindings(arch,sparseopts,prob,mapping):
    # Parse the dense problem
    # - data_space_dict_list
    # - (omitted) prob_coeff_list
    # - (omitted) prob_instance_rank_sizes
    # - (omitted) prob_instance_densities
    data_space_dict_list, _, _, _=data_space_dict_list_from_sl_prob(prob)    
    
    # Bind representation-format processing interfaces to architectural buffers
    # (mapping- and problem-dependent approach)
    # - fmt_iface_bindings
    # - (omitted) pgens
    # - (omitted) buffer_loop_binding
    # - loop_to_iface_map
    fmt_iface_bindings, _, _, loop_to_iface_map=bind_format_iface(arch, mapping, prob, sparseopts)

    # Bind action-optimization SAFs to archtiectural buffers
    # - skip_bindings
    skip_bindings=bind_action_optimization(arch, mapping, prob, sparseopts, fmt_iface_bindings, loop_to_iface_map)

    print("skip_bindings:",skip_bindings)

    return fmt_iface_bindings, skip_bindings, data_space_dict_list

def get_buffer_dataspace_to_fmt_access_bindings_from_buffer_dataspace_to_fmt_layout_bindings(buffer_dataspace_to_fmt_layout_binding, data_space_dict_list, flat_arch, buffer_loop_binding):
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
    last_resident_buffer={dtype:top_lvl_buffer for dtype in data_space_dict_list}

    # Re-bind fibers to the buffer levels at which they are accessed
    for buffer in flat_arch:
        buffer_kept_data_spaces=buffer_loop_binding[buffer]['data-spaces']
        for dtype in data_space_dict_list:
            if dtype in buffer_kept_data_spaces:
                # For each datatype resident in this buffer level,
                upper_buffer=last_resident_buffer[dtype]
                if upper_buffer != buffer:
                    #if this buffer level is **not** top-level memory,
                    if dtype in buffer_dataspace_to_fmt_layout_binding[upper_buffer]['representation-format']:
                        # and if there are any sparse fibers at this buffer level for this datatype,
                        # then omit this tile from the lowest higher buffer level which keeps this datatype
                        buffer_dtype_tile=buffer_dataspace_to_fmt_layout_binding[buffer]['representation-format'][dtype]['ranks']                        
                        upper_buffer_dtype_tile=copy.deepcopy(buffer_dataspace_to_fmt_layout_binding[upper_buffer]['representation-format'][dtype]['ranks'])
                        
                        # TODO: more efficient approach to suffix pruning
                        num_buffer_dtype_tile_fibers=len(buffer_dtype_tile)
                        num_upper_buffer_dtype_tile_fibers=len(upper_buffer_dtype_tile)
                        num_traversed_upper_buffer_dtype_tile_fibers=num_upper_buffer_dtype_tile_fibers-num_buffer_dtype_tile_fibers
                        traversed_upper_buffer_dtype_tile_fibers=upper_buffer_dtype_tile[0:num_traversed_upper_buffer_dtype_tile_fibers]

                        buffer_dataspace_to_fmt_access_binding[upper_buffer]['representation-format'][dtype]['ranks']=traversed_upper_buffer_dtype_tile_fibers

                last_resident_buffer[dtype]=buffer

        

    return buffer_dataspace_to_fmt_access_binding

def bind_format_iface(arch, mapping, prob, sparseopts):
    '''Bind format interfaces to buffers, loops, ranks, formats & address arithmetic'''

    # Extract data-space, mapping & flattened architecture info
    data_space_dict_list, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities=data_space_dict_list_from_sl_prob(prob)
    buffer_loop_binding=buffer_loop_binding_from_sl_arch_and_map(arch, mapping, prob_instance_rank_sizes, data_space_dict_list)
    flat_arch=flatten_arch_wrapper(arch)
    pgens, delegation_table=bind_pgens(arch, mapping, prob)
    buffer_dataspace_to_fmt_layout_binding=get_buffer_dataspace_to_fmt_layout_bindings_from_sparseopts(sparseopts)
    buffer_dataspace_to_fmt_access_binding=get_buffer_dataspace_to_fmt_access_bindings_from_buffer_dataspace_to_fmt_layout_bindings(buffer_dataspace_to_fmt_layout_binding, data_space_dict_list, flat_arch, buffer_loop_binding)

    loop_to_iface_map={buffer:{dtype:{} for dtype in data_space_dict_list} for buffer in flat_arch}

    #print(buffer_loop_binding)

    fmt_ifaces={buffer:{dtype:[] for dtype in data_space_dict_list} for buffer in flat_arch}

    for buffer in flat_arch:
        #print("Entering", buffer)
        # For each buffer, get 
        #loop_order=copy.deepcopy(buffer_loop_binding[buffer]['loops']['permutation'])
        #loop_order.reverse()
        loop_buffer_kept_data_spaces=buffer_loop_binding[buffer]['data-spaces']
        for dtype in data_space_dict_list:
            #print("Entering",dtype)
            #print(loop_buffer_kept_data_spaces)
            if dtype in loop_buffer_kept_data_spaces:
                # For each combination of buffer and kept datatype,
                # - Compute pointers to pgens bound to non-trivial loops
                buffer_dtype_pgens=pgens[buffer][dtype]
                nontrivial_pgen_ptrs=[]
                nontrivial_pgen_is_bound=[]
                data_space_projection=data_space_dict_list[dtype]['projection']
                data_space_sop_is_bound=[False for expr in data_space_projection] # Initialize data-space projection SOP binding tracking
                fmt_ifaces_temp=[]
                fmt_access_rank_is_bound=[]
                for idx in range(len(buffer_dtype_pgens)):
                    # Initialize pgen binding tracking
                    loop_ptr=buffer_dtype_pgens[idx]
                    #print(buffer_loop_binding[loop_ptr['loop_buffer']]['loops']['non-trivial'][loop_ptr['rank']])
                    if buffer_loop_binding[loop_ptr['loop_buffer']]['loops']['non-trivial'][loop_ptr['rank']]:
                        nontrivial_pgen_ptrs.append(idx)
                        nontrivial_pgen_is_bound.append(False)
                
                # - First-pass binding: bind flattened sparseopts fibers which call out specific ranks, to the associated pgens and to a format interface
                if dtype in buffer_dataspace_to_fmt_access_binding[buffer]['representation-format']:
                    fmt_access_binding=buffer_dataspace_to_fmt_access_binding[buffer]['representation-format'][dtype]['ranks']
                    fmt_access_rank_is_bound=[False for rank in fmt_access_binding]
                    for fdx in range(len(fmt_access_binding)):
                        fiber=fmt_access_binding[fdx]
                        if 'flattened-rankIDs' in fiber:
                            fmt_access_rank_is_bound[fdx]=True
                            # -- Pass 1a: create a format interface for each fiber which comprises flattened rank IDs
                            fiber_layout=fiber['flattened-rankIDs']
                            #print(prob_coeff_list)
                            fmt=fiber['format']
                            ranks=data_space_rank_list_from_SOP(fiber_layout, prob_coeff_list)
                            pgen_idxs=[]
                            at_least_one_nontrivial_rank=False
                            for target_rank in ranks:
                                pgen_idx, nontrivial_pgen_is_bound, is_nontrivial = first_unbound_nontrival_pgen_idx_by_rank(target_rank, buffer_dtype_pgens, nontrivial_pgen_ptrs, nontrivial_pgen_is_bound)
                                at_least_one_nontrivial_rank = at_least_one_nontrivial_rank or is_nontrivial
                                pgen_idxs.append(pgen_idx)
                            assert(at_least_one_nontrivial_rank)

                            # -- Pass 1b: select for dataspace projection expressions which project onto this format interface
                            dataspace_proj_onto_fmt_iface=[]
                            #print("DICT:",data_space_dict_list[dtype]['projection'])
                            for idx in range(len(data_space_projection)):
                                expr=data_space_projection[idx]
                                #print("EXPR",expr)
                                expr_ranks=data_space_rank_list_from_SOP(expr, prob_coeff_list)
                                #print("EXPR_RANKS",expr_ranks)

                                flat_fiber_ranks_contain_expr_ranks=False #TODO: var name is no longer correct
                                #print("RANKS",ranks)
                                for rank in expr_ranks:
                                    # Determine whether a dataspace projection expression projects onto this format interface
                                    #print(rank,ranks,rank not in ranks)
                                    if rank in ranks:
                                        flat_fiber_ranks_contain_expr_ranks=True
                                
                                if flat_fiber_ranks_contain_expr_ranks:
                                    dataspace_proj_onto_fmt_iface.append(expr)
                                    data_space_sop_is_bound[idx]=True

                            # Construct format interface
                            #print("PROJECTION_ISSUE:",dataspace_proj_onto_fmt_iface)
                            fmt_ifaces_temp.append({'fiber_layout':fiber_layout,'format':fmt,'ranks':ranks,'pgens':pgen_idxs,'projection':dataspace_proj_onto_fmt_iface})
                            #print("FORMAT:",fmt)

                    
                    # - Second-pass binding: bind dataspace projection SOPs (the ones not bound in the first-pass) to pgens and format interfaces; infer formats
                    for idx in range(len(data_space_projection)):
                        if not data_space_sop_is_bound[idx]:
                            expr=data_space_projection[idx]
                            expr_ranks=data_space_rank_list_from_SOP(expr, prob_coeff_list)
                            pgen_idxs=[]
                            fiber_layout=expr                    
                            at_least_one_nontrivial_rank=False
                            for target_rank in expr_ranks:
                                # -- Pass 2a: bind dataspace projection SOPs (the ones not bound in the first-pass) to pgens and format interfaces
                                pgen_idx, _, is_nontrivial = first_unbound_nontrival_pgen_idx_by_rank(target_rank, buffer_dtype_pgens, nontrivial_pgen_ptrs, nontrivial_pgen_is_bound, update_is_bound=False)
                                at_least_one_nontrivial_rank = at_least_one_nontrivial_rank or is_nontrivial
                                pgen_idxs.append(pgen_idx)
                            if at_least_one_nontrivial_rank:
                                # --- Commit SOP bindings only if at least one rank in SOP can bind to a non-trivial pgen
                                for pgen_idx in pgen_idxs:
                                    if pgen_idx in nontrivial_pgen_ptrs:
                                        nontrivial_pgen_is_bound[nontrivial_pgen_ptrs.index(pgen_idx)]=True
                                # Construct format interface
                                fmt_ifaces_temp.append({'fiber_layout':fiber_layout,'ranks':expr_ranks,'pgens':pgen_idxs,'projection':expr})                        

                            # Even if dataspace projection SOP cannot bind to a non-trivial pgen and a format interface, still mark it as bound to avoid revisiting.
                            data_space_sop_is_bound[idx]=True

                    # -- Pass 2b: infer formats

                    #print("fmt_access_rank_is_bound (PRE)",fmt_access_rank_is_bound)
                    #print("data_space_sop_is_bound (PRE)",data_space_sop_is_bound)
                    for idx in range(len(fmt_access_binding)):
                        #print("idx:",idx)
                        if not fmt_access_rank_is_bound[idx]:
                            seek_fmt_iface=True
                            jdx=0
                            while(seek_fmt_iface and jdx < len(fmt_ifaces_temp)):
                                #print("jdx:",jdx)
                                if not 'format' in fmt_ifaces_temp[jdx]:
                                    seek_fmt_iface=False
                                    fmt_ifaces_temp[jdx]['format']=fmt_access_binding[idx]['format']
                                    fmt_access_rank_is_bound[idx]=True
                                jdx+=1    

                    # - Third-pass cleanup: delete candidate format interfaces which were not successfully bound to a metadata format
                    cleanup_idxs=[]
                    for idx in range(len(fmt_ifaces_temp)):
                        # -- Pass 3a: mark format interfaces for cleanup
                        if 'format' not in fmt_ifaces_temp[idx]:
                            cleanup_idxs.append(idx)
                    total_removed=0
                    for jdx in range(len(cleanup_idxs)):
                        # -- Pass 2b: perform cleanup of marked idxs
                        idx=cleanup_idxs[jdx]-total_removed
                        fmt_ifaces_temp=fmt_ifaces_temp[0:idx] + fmt_ifaces_temp[(idx+1):]
                        total_removed+=1
                                            

                fmt_ifaces[buffer][dtype].extend(fmt_ifaces_temp)

            #print("buffer",buffer)
            #print("dtype",dtype)
            for idx in range(len(fmt_ifaces[buffer][dtype])):
                fmt_iface=fmt_ifaces[buffer][dtype][idx]
                for pgen_idx in fmt_iface['pgens']:
                    loop_rank=pgens[buffer][dtype][pgen_idx]['rank']
                    loop_buffer=pgens[buffer][dtype][pgen_idx]['loop_buffer']
                    #print("loop_buffer",loop_buffer)
                    loop_to_iface_map[loop_buffer][dtype][loop_rank]={'fmt_iface':idx, 'buffer':buffer, 'dtype':dtype}
                    
                #print("data_space_sop_is_bound (POST)",data_space_sop_is_bound)
                #print("fmt_access_rank_is_bound (POST)",fmt_access_rank_is_bound)
                #print("nontrivial_pgen_is_bound",nontrivial_pgen_is_bound)

    #print(loop_to_iface_map)

    #print(fmt_ifaces)   
    return copy.deepcopy(fmt_ifaces), pgens, buffer_loop_binding, loop_to_iface_map

def get_skip_format_interface_bindings(target_buffer, target_dtype, condition_buffer, condition_dtype, loop_to_iface_map):
    
    fmt_iface_list=[]

    for loop_buffer in loop_to_iface_map:
        if (target_dtype in loop_to_iface_map[loop_buffer]) and (condition_dtype in loop_to_iface_map[loop_buffer]):
            target_dtype_loop_ranks=loop_to_iface_map[loop_buffer][target_dtype]
            condition_dtype_loop_ranks=loop_to_iface_map[loop_buffer][condition_dtype]

            for target_rank in target_dtype_loop_ranks:
                if target_dtype_loop_ranks[target_rank]['buffer']==target_buffer:
                    target_fmt_iface=target_dtype_loop_ranks[target_rank]['fmt_iface']
                    if (target_rank in condition_dtype_loop_ranks) and (condition_dtype_loop_ranks[target_rank]['buffer']==condition_buffer):
                        condition_fmt_iface=condition_dtype_loop_ranks[target_rank]['fmt_iface']
                        fmt_iface_list.append({'target':{'buffer':target_buffer, 'dtype':target_dtype, 'fmt_iface':target_fmt_iface}, 'condition':{'buffer':condition_buffer, 'dtype':condition_dtype, 'fmt_iface':condition_fmt_iface}, 'loop_binding':{'loop_buffer':loop_buffer, 'rank':target_rank}})

    return fmt_iface_list

def bind_action_optimization(arch, mapping, prob, sparseopts, fmt_ifaces, loop_to_iface_map):
    # Extract data-space, mapping & flattened architecture info
    data_space_dict_list, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities=data_space_dict_list_from_sl_prob(prob)
    buffer_loop_binding=buffer_loop_binding_from_sl_arch_and_map(arch, mapping, prob_instance_rank_sizes, data_space_dict_list)
    flat_arch=flatten_arch_wrapper(arch)
    pgens, delegation_table=bind_pgens(arch, mapping, prob)
    buffer_dataspace_to_fmt_layout_binding=get_buffer_dataspace_to_fmt_layout_bindings_from_sparseopts(sparseopts)

    action_optim_blacklist=['gating']

    raw_skips=[]

    for target_buffer in flat_arch:
        if 'action-optimization' in buffer_dataspace_to_fmt_layout_binding[target_buffer]:
            buffer_action_optim=buffer_dataspace_to_fmt_layout_binding[target_buffer]['action-optimization']

            for action_optim in buffer_action_optim:
                if action_optim['type']=='skipping':
                    for option in action_optim['options']:
                        target_dtype=option['target']
                        condition_dtypes=option['condition-on']

                        for condition_dtype in condition_dtypes:
                            condition_buffer=delegation_table[target_buffer][condition_dtype]

                            fmt_iface_list=get_skip_format_interface_bindings(target_buffer, target_dtype, condition_buffer, condition_dtype, loop_to_iface_map)
                            raw_skips.extend(fmt_iface_list)

    print(raw_skips)
    return raw_skips