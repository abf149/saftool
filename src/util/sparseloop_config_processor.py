import yaml
import copy

def load_config_yaml(config_filename):
    """Load a Sparseloop YAML-format config file
    
    Keyword arguments:
    config_filename -- the absolute or relative filepath
    """
    config=[]

    with open(config_filename,'r') as config_fp:
        config=yaml.safe_load(config_fp)
    
    return config

# Data-space parsing routines

def data_space_rank_list_from_product(product, prob_coeff_list):
    """ Extract a list of ranks that project onto a data-space, from a particular product in the data-space's projection expression.

    Keyword arguments:
    product -- the data-space's projection expression
    prob_coeff_list -- a list of the constant coefficients associated with this problem
    """

    data_space_rank_list=[]

    #print("PRODUCT")
    #print(product)
    #print(prob_coeff_list)
    for fact in product:
        #print("FACT")
        #print(fact)
        if fact not in prob_coeff_list:
            data_space_rank_list.append(fact)    

    return data_space_rank_list

def data_space_rank_list_from_SOP(sop, prob_coeff_list):
    data_space_rank_list=[]

    for product in sop:
        product_ranks=data_space_rank_list_from_product(product, prob_coeff_list)
        data_space_rank_list.extend(product_ranks)

    return data_space_rank_list    

def data_space_rank_list_from_projection(projection, prob_coeff_list):
    """ Extract a list of ranks that project onto a data-space, from the data-space's projection expression.

    Keyword arguments:
    projection -- the data-space's projection expression
    prob_coeff_list -- a list of the constant coefficients associated with this problem
    """

    data_space_rank_list=[]
    for sop in projection:
        sop_ranks=data_space_rank_list_from_SOP(sop, prob_coeff_list)
        data_space_rank_list.extend(sop_ranks)

    return data_space_rank_list


def data_space_dict_list_from_sl_prob(prob):
    """ Extract a list of data-space representations from the sparseloop prob dict
    Keyword arguments:
    prob -- the Sparseloop prob config
    """

    data_space_types_dict={}
    prob_coeff_list={coeff['name']:coeff['default'] for coeff in prob['problem']['shape']['coefficients']}
    prob_instance_rank_sizes={rank:prob['problem']['instance'][rank] for rank in prob['problem']['instance'] if rank != 'densities'}
    prob_instance_densities=prob['problem']['instance']['densities']
    data_space_idx=0
    for data_space in prob['problem']['shape']['data-spaces']:
        if 'read-write' not in data_space:
            data_space['read-write']=False
        data_space_rank_list=data_space_rank_list_from_projection(data_space['projection'], prob_coeff_list)
        data_space_types_dict[data_space['name']]={'idx':data_space_idx,'projection':data_space['projection'],'rank-list':data_space_rank_list,'read-write':data_space['read-write']}
        data_space_idx += 1

    return data_space_types_dict, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities

# Mapping parsing routines

def parse_sl_mapping(mapping, prob_instance_rank_sizes, data_space_dict_list):
    """ Reformat the Sparseloop mapping file.

    Keyword arguments:
    mapping -- The Sparseloop map config
    """

    parsed_mapping={}

    type_blacklist=['spatial']

    for attrib in mapping['mapping']:
        # For each mapping config line
        attrib_type=attrib['type']
        if attrib['type'] not in type_blacklist:
            buffer=attrib['target']
            if buffer not in parsed_mapping:
                parsed_mapping[buffer]={}
                parsed_mapping[buffer]['data-spaces']=list(data_space_dict_list.keys())
            if attrib_type=='bypass':
                # Collect data-space bypass info @ buffer-level
                parsed_mapping[buffer]['data-spaces']=attrib['keep']
            elif attrib_type=='temporal':
                # Collect permutation & factor info @ buffer-level

                # Extract loops
                loops={'permutation':[rank for rank in attrib['permutation']]}

                # Extract factors
                loops['factors']={factor_expr.split('=')[0]:int(factor_expr.split('=')[1]) for factor_expr in attrib['factors'].split(' ')}

                # Introduce implicit factors
                for rank in prob_instance_rank_sizes:
                    if rank not in loops['factors']:
                        loops['factors'][rank]=1

                # Identify non-trivial loops (factor==1 or else residual (factor==0))
                # (need to do this before we compute residuals)
                loops['non-trivial']={rank:(loops['factors'][rank]!=1) for rank in loops['factors']}

                parsed_mapping[buffer]['loops']=loops

    # Account for residuals (rank length=0) in each rank
    for rank in prob_instance_rank_sizes:
        rank_len=prob_instance_rank_sizes[rank]
        # For each problem rank - 
        # First-pass: compute residual
        for buffer in parsed_mapping:
            if parsed_mapping[buffer]['loops']['factors'][rank] != 0:
                # in computing residual, skip loop with residual factor placeholder
                rank_len=rank_len/parsed_mapping[buffer]['loops']['factors'][rank]
        
        # Second-pass: detect loop with residual factor
        for buffer in parsed_mapping:
            if parsed_mapping[buffer]['loops']['factors'][rank] == 0:
                # replace residual factor placeholder with residual
                # TODO: currently no support for factors that are no factors
                assert(rank_len == int(rank_len))
                parsed_mapping[buffer]['loops']['factors'][rank] = int(rank_len)

    return parsed_mapping

# Architecture parsing routines

def flatten_arch_recursive(hierarchical_arch):
    '''Recursive unwrapping of Sparseloop architecture'''
    res={}
    for parent in hierarchical_arch:
        if 'local' in parent:
            # Append buffer-level names at this hierarchical level
            for lvl in parent['local']:
                if lvl['name'] != 'MAC':
                    res[lvl['name']]={attrib:lvl[attrib] for attrib in lvl if attrib != 'name'}
        if 'subtree' in parent:
            # Recurse to list of buffer subtrees below this node
            res=dict(res,**flatten_arch_recursive(parent['subtree']))

    return res

def flatten_arch_wrapper(arch):
    '''Wrapper for recursive flattening of Sparseloop architecture config'''
    return flatten_arch_recursive(arch['architecture']['subtree'])

def buffer_loop_binding_from_sl_arch_and_map(arch, mapping, prob_instance_rank_sizes, data_space_dict_list):
    parsed_mapping=parse_sl_mapping(mapping, prob_instance_rank_sizes, data_space_dict_list)

    buffer_hierarchy=flatten_arch_wrapper(arch)

    for buffer in buffer_hierarchy:
        buffer_hierarchy[buffer]['loops']=parsed_mapping[buffer]['loops']
        buffer_hierarchy[buffer]['data-spaces']=parsed_mapping[buffer]['data-spaces']

    return buffer_hierarchy

# Sparseopts parsing routines

def get_buffer_dataspace_to_fmt_layout_bindings_from_sparseopts(sparseopts):
    buffer_dataspace_to_fmt_layout_binding={}
    for target_buffer_dict in sparseopts['sparse_optimizations']['targets']:
        # Extract per-arch-level SAFs
        target_buffer=target_buffer_dict['name']
        buffer_dataspace_to_fmt_layout_binding[target_buffer]={'representation-format':{}}
        if 'representation-format' in target_buffer_dict:
            target_data_space_dicts=target_buffer_dict['representation-format']['data-spaces']
            for target_data_space_dict in target_data_space_dicts:
                target_data_space=target_data_space_dict['name']
                buffer_dataspace_to_fmt_layout_binding[target_buffer]['representation-format'][target_data_space]={attrib:target_data_space_dict[attrib] for attrib in target_data_space_dict if attrib != 'name'}
        if 'action-optimization' in target_buffer_dict:
            buffer_dataspace_to_fmt_layout_binding[target_buffer]['action-optimization']=target_buffer_dict['action-optimization']

    return buffer_dataspace_to_fmt_layout_binding

def get_buffer_dataspace_to_fmt_access_bindings_from_buffer_dataspace_to_fmt_layout_bindings(buffer_dataspace_to_fmt_layout_binding, data_space_dict_list, flat_arch, buffer_loop_binding):
    ''' Generate buffer/datapsace/format-access bindings from buffer/dataspace/format-layout bindings.

    Sparseloop sparseopts spec binds a fibertree memory layout to a datatype and buffer-level.
    Not all fibers resident at a buffer-level are traversed at that buffer-level; some fibers are part of a tile which will be filled into lower memory.
    This function consumes sparseopts-style fiber bindings and re-binds fibers to the memory levels where they are traversed.
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
                    #if this is not top-level memory,
                    if dtype in buffer_dataspace_to_fmt_layout_binding[upper_buffer]['representation-format']:
                        # and if there are any sparse fibers at this buffer level,
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


# Bindings

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

    for loop_buffer in flat_arch:
        loop_buffer_kept_data_spaces=buffer_loop_binding[loop_buffer]['data-spaces']
        loop_factors=buffer_loop_binding[loop_buffer]['loops']['factors']
        for dtype in data_space_dict_list:
            # For each combination of buffer and datatype, determine which buffer (pgen_buffer) to bind pgens to:
            if dtype in loop_buffer_kept_data_spaces:
                # (either this buffer or the lowest higher buffer which keeps dtype.)
                last_buffer[dtype]=loop_buffer
            pgen_buffer=last_buffer[dtype]
            
            # Then, for each loop that is bound to loop_buffer AND projects onto dtype, create a pgen bound to that loop AND pgen_buffer.
            # Each loop is represented by a rank and the buffer it is bound to, rather than by the usual rank + tiling-level notation (i.e. M0, R2, etc.)
            dtype_projection_ranks=data_space_dict_list[dtype]['rank-list']
            pgens[pgen_buffer][dtype].extend([{'rank':rank,'loop_buffer':loop_buffer} for rank in loop_factors if rank in dtype_projection_ranks])

    return pgens

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

def bind_format_iface(arch, mapping, prob, sparseopts):
    '''Bind format interfaces to buffers, loops, ranks, formats & address arithmetic'''

    # Extract data-space, mapping & flattened architecture info
    data_space_dict_list, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities=data_space_dict_list_from_sl_prob(prob)
    buffer_loop_binding=buffer_loop_binding_from_sl_arch_and_map(arch, mapping, prob_instance_rank_sizes, data_space_dict_list)
    flat_arch=flatten_arch_wrapper(arch)
    pgens=bind_pgens(arch, mapping, prob)
    buffer_dataspace_to_fmt_layout_binding=get_buffer_dataspace_to_fmt_layout_bindings_from_sparseopts(sparseopts)
    buffer_dataspace_to_fmt_access_binding=get_buffer_dataspace_to_fmt_access_bindings_from_buffer_dataspace_to_fmt_layout_bindings(buffer_dataspace_to_fmt_layout_binding, data_space_dict_list, flat_arch, buffer_loop_binding)

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
                #print("data_space_sop_is_bound (POST)",data_space_sop_is_bound)
                #print("fmt_access_rank_is_bound (POST)",fmt_access_rank_is_bound)
                #print("nontrivial_pgen_is_bound",nontrivial_pgen_is_bound)

    #print(fmt_ifaces)   
    return fmt_ifaces         

"""

class FormatSAF:
    '''
    Represents an abstract Format SAF
    
    ...

    Attributes
    ----------
    sparseopts_representation_format_structure : dict
        Format SAF attributes extracted from sparseopts. Abstract object represented as dict of per-dataspace tensor representation descriptors.
    level_name : str
        Name of architectural level at which this SAF is applied
    '''

    def __init__(self, sparseopts_representation_format_structure, level_name):
        self.sparseopts_representation_format_structure=sparseopts_representation_format_structure
        self.level_name=level_name
        self.dataspace_format_map={}
        for dataspace_format in self.sparseopts_representation_format_structure:
            # Build a mapping from dataspace to list of rank formats
            self.dataspace_format_map[dataspace_format['name']] = [rank['format'] for rank in dataspace_format['ranks']]

    def __str__(self):
        #str_val = "- Arch level: " + self.level_name + "\n" + "  - Format SAF:" + "\n"
        str_val = ""
        for dataspace in self.dataspace_format_map:
            str_val += "    - Dataspace: " + dataspace + "\n" + "      - Format: " + str(self.dataspace_format_map[dataspace]) + "\n"
        return str_val

class SAFSpec:
    '''
    Represent the SAF specifications in a Sparseloop config.
    
    ...
    
    Attributes
    ----------
    sparseopts_filename : str
        Sparseloop sparseopts filename
    '''

    def __init__(self, sparseopts_filename):
        # Parse YAML sparseopts config file
        self.sparseopts=load_config_yaml(sparseopts_filename)['sparse_optimizations']
        sparseopt_targets=self.sparseopts['targets']
        self.arch_saf_map={}
        self.arch_dataspace_map={}
        self.dataspace_arch_map={}
        #arch_levels=[targetObj['name'] for targetObj in sparseopt_targets]
        for targetObj in sparseopt_targets:
            # Extract per-arch-level SAFs
            arch_lvl=targetObj['name']
            self.arch_saf_map[arch_lvl] = {'SkipSAF':None,'GateSAF':None,'FormatSAF':None}
            if 'representation-format' in targetObj:
                self.arch_saf_map[arch_lvl]['FormatSAF'] = FormatSAF(targetObj['representation-format']['data-spaces'],arch_lvl)
                for dataspace_format in targetObj['representation-format']['data-spaces']:
                    # Build reverse-mapping from dataspace to arch levels which keep the dataspace
                    if dataspace_format['name'] in self.dataspace_arch_map:
                        self.dataspace_arch_map[dataspace_format['name']].append(arch_lvl)
                    else:
                        self.dataspace_arch_map[dataspace_format['name']]=[arch_lvl]

    def getDataspaceArchMap(self):
        return self.dataspace_arch_map

    def getArchLevels(self):
        '''Return a list of architectural levels in the topology'''
        return list(self.arch_saf_map.keys())

    def getArchLevelDataspaces(self, arch_lvl):
        '''
        Return a list of dataspaces kept by a particular architectural level

        Keyword arguments:
        arch_lvl -- architecture level
        '''

        if self.arch_saf_map[arch_lvl]['FormatSAF'] is None:
            return []

        return self.arch_saf_map[arch_lvl]['FormatSAF'].dataspace_format_map.keys()

    def getArchLevelSAFs(self, arch_lvl):
        '''
        Return the SAF instances associated with an architecture level

        Keyword arguments:
        arch_lvl -- architectural level
        '''
        return self.arch_saf_map[arch_lvl]

    def __str__(self):
        str_val = "SAFSpec\n"
        str_val += "- Architecture level to SAF mapping:\n\n"
        for arch_lvl in self.arch_saf_map:
            str_val += "  - " + arch_lvl + ":" + "\n\n"
            if not (self.arch_saf_map[arch_lvl]['FormatSAF'] is None):
                str_val += str(self.arch_saf_map[arch_lvl]['FormatSAF']) + "\n"
        str_val += "- Dataspace to architecture mapping:\n\n"
        for dataspace in self.dataspace_arch_map:
            str_val += "  - " + dataspace + ": " + str(self.dataspace_arch_map[dataspace]) + "\n"
        return str_val

"""