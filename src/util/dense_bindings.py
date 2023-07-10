from util.parse import *

# Dense bindings

def bind_pgens(arch, mapping, prob):
    '''Bind pgens to loops & buffers'''

    # Extract data-space, mapping & flattened architecture info
    data_space_dict_list, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities=data_space_dict_list_from_sl_prob(prob)
    buffer_loop_binding=buffer_loop_binding_from_sl_arch_and_map(arch, mapping, prob_instance_rank_sizes, data_space_dict_list)
    flat_arch=flatten_arch_wrapper(arch)

    top_lvl_buffer=list(flat_arch.keys())[0]

    # Create pgens and bind them to loops and buffer levels
    # The loop (which the pgen is bound to) may itself be bound to a different buffer level than the pgen
    pgens={buffer:{dtype:[] for dtype in data_space_dict_list} for buffer in flat_arch}
    last_buffer={dtype:top_lvl_buffer for dtype in data_space_dict_list}

    delegation_table={buffer:{dtype:buffer for dtype in data_space_dict_list} for buffer in flat_arch}

    for loop_buffer in flat_arch:
        loop_buffer_kept_data_spaces=buffer_loop_binding[loop_buffer]['data-spaces']
        loop_factors=buffer_loop_binding[loop_buffer]['loops']['factors']
        for dtype in data_space_dict_list:
            # For each combination of buffer and datatype, determine which buffer (pgen_buffer) to bind pgens to:
            if dtype in loop_buffer_kept_data_spaces:
                # (either this buffer or the lowest higher buffer which keeps dtype.)
                last_buffer[dtype]=loop_buffer
            pgen_buffer=last_buffer[dtype]

            delegation_table[loop_buffer][dtype]=pgen_buffer
            
            # Then, for each loop that is bound to loop_buffer AND projects onto dtype, create a pgen bound to that loop AND pgen_buffer.
            # Each loop is represented by a rank and the buffer it is bound to, rather than by the usual rank + tiling-level notation (i.e. M0, R2, etc.)
            dtype_projection_ranks=data_space_dict_list[dtype]['rank-list']
            pgens[pgen_buffer][dtype].extend([{'rank':rank,'loop_buffer':loop_buffer} for rank in loop_factors if rank in dtype_projection_ranks])

    #print("Delegation table",delegation_table)

    return pgens, delegation_table

def first_unbound_nontrival_pgen_idx_by_rank(target_rank, buffer_dtype_pgens, nontrivial_pgen_ptrs, nontrivial_pgen_is_bound, update_is_bound=True):
    #print(target_rank)
    #print(buffer_dtype_pgens)
    #print(nontrivial_pgen_ptrs)
    #print(nontrivial_pgen_is_bound)

    '''Find the index of the outer-most (highest-level) non-trivial pgen which is not yet bound to a format interface'''
    for jdx in range(len(nontrivial_pgen_ptrs)):
        if not nontrivial_pgen_is_bound[jdx]:
            idx=nontrivial_pgen_ptrs[jdx]
            loop_ref=buffer_dtype_pgens[idx]
            if loop_ref['rank']==target_rank:
                if update_is_bound:
                    nontrivial_pgen_is_bound[jdx]=True
                return idx, nontrivial_pgen_is_bound, True # last return value indicates that a non-trivial pgen was found

    # If we made it this far, there is no unbound non-trivial pgen. Widen the search to include trivial pgens.
    for idx in range(len(buffer_dtype_pgens)):
        #if not nontrivial_pgen_is_bound[jdx]:
        #    idx=nontrivial_pgen_ptrs[jdx]
        loop_ref=buffer_dtype_pgens[idx]
        if loop_ref['rank']==target_rank:
        #    nontrivial_pgen_is_bound[jdx]=True
            return idx, nontrivial_pgen_is_bound, False # trivial pgen found