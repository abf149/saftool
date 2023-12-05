'''Parse Sparseloop YAML files'''

import core.parse as pr_
from core.helper import info,warn,error

'''SAFInfer parsing routines'''
# Data-space parsing routines
# Terminology for dataspace projections
# - Projection expression: a collection of SOP expressions projecting the problem dimensions onto each rank of a dataspace's
#                          tensor
#     - Example: [ [[coef_1,H],[coef_2,W]], [[M]] ]
# - Sum-of-product (SOP) expression - represents the projection of problem dimensions onto a single rank
#                                     of a dataspace's tensor. Takes the form of an affine transformation
#                                     of problem dimensions, i.e. sum of coefficient*problem_dimension terms
#     - Example: [[coef_1,H],[coef_2,W]]
# - Product expression - a single coefficient*problem_dimension term
#     - Example: [coef_1,H] or [[M]] (implicit coefficient of 1)

'''
custom_taxonomic_specifications:
  dense_buffer_format_interfaces:
  - name: psum
    dataspaces:
    - name: Outputs
      dummy_format_interfaces:
      - flattened-rankIDs: [ [ C ] ]
      - flattened-rankIDs: [ [ M ] ] 
'''

def flatten_SOP_ranks_list(lst):
    # Flatten nested lists into a single list.
    return [item for sublist in lst for item in \
                (flatten_SOP_ranks_list(sublist) if isinstance(sublist, list) else [sublist])]

def parse_dense_fmt_iface_settings(user_attributes):
    res={}
    dense_buffer_format_interfaces=user_attributes['custom_taxonomic_specifications']['dense_buffer_format_interfaces']
    for buffer_settings in dense_buffer_format_interfaces:
        buffer=buffer_settings['name']
        dataspaces=buffer_settings['dataspaces']
        for dtype_settings in dataspaces:
            dtype=dtype_settings['name']
            fmt_ifaces = \
                [ranks_list_dict['flattened-rankIDs'] \
                    for ranks_list_dict in dtype_settings['dummy_format_interfaces']]

            res.setdefault(buffer,{})[dtype]=fmt_ifaces

    return res


def data_space_rank_list_from_product(product, prob_coeff_list):
    """ Extract a partial list of problem dimensions that project onto a dataspace rank, from a particular product expression. Excludes coefficients.

    Keyword arguments:
    product -- the product expression
    prob_coeff_list -- a complete list of the constant coefficients associated with this problem
    """

    data_space_rank_list=[]

    for fact in product:
        if fact not in prob_coeff_list:
            data_space_rank_list.append(fact)    

    return data_space_rank_list

def data_space_rank_list_from_SOP(sop, prob_coeff_list):
    """ Extract a complete list of problem dimensions that project onto a dataspace rank, from a particular SOP expression. Excludes coefficients.

    Keyword arguments:
    product -- the SOP expression
    prob_coeff_list -- a complete list of the constant coefficients associated with this problem
    """

    data_space_rank_list=[]

    for product in sop:
        product_ranks=data_space_rank_list_from_product(product, prob_coeff_list)
        data_space_rank_list.extend(product_ranks)

    return data_space_rank_list    

def data_space_rank_list_from_projection(projection, prob_coeff_list):
    """ Extract a complete list of problem dimensions that project onto a dataspace, from a particular projection expression. Excludes coefficients.

    Keyword arguments:
    product -- the projection expression
    prob_coeff_list -- a complete list of the constant coefficients associated with this problem
    """

    data_space_rank_list=[]
    for sop in projection:
        sop_ranks=data_space_rank_list_from_SOP(sop, prob_coeff_list)
        data_space_rank_list.extend(sop_ranks)

    return data_space_rank_list


def data_space_dict_list_from_sl_prob(prob):
    """ Extract a list of data-space representations from the sparseloop prob dict\n
    Keyword arguments:\n
    prob -- the Sparseloop problem config\n\n

    return:\n
    data_space_dict_list -- Enumerate prob datatypes, include metadata regarding ranks, projects, & read/write support.\n
    - Example:\n
    - {'Weights': \n
        {'idx': 0, \n
        'projection': [[['C']], [['M']], [['G']], [['R']], [['S']]], \n
        'rank-list': ['C', 'M', 'G', 'R', 'S'], \n
        'read-write': False}, \n
       'Inputs': \n
        {'idx': 1,\n
       ... \n
        } \n
       'Outputs': \n
        {'idx': 2, \n
        ... \n
         'read-write': True \n
        } \n
       } \n

    prob_coeff_list -- dict of coefficients in the projection formula, to distinguish from ranks.\n
    - TODO: refactor name to be _dict not _list\n
    - Example:\n
    - {'Wstride': 1, 'Hstride': 1, 'Wdilation': 1, 'Hdilation': 1}\n
    prob_instance_rank_sizes -- number of elements (words) along each problem rank\n
    - Example:\n
    - {'M': 64, 'E': 32, 'F': 32, 'R': 1, 'S': 1, 'N': 1, 'G': 1, 'C': 64} \n
    prob_instance_densities -- \n
    - Example:\n
    - {'Inputs': \n
       {'distribution': 'hypergeometric', \n
        'density': 0.73\n
       }, \n
       'Weights': \n
       {'distribution': 'hypergeometric', \n
        'density': 0.52\n
       }\n
      } \n
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
    '''
    Wrapper for recursive flattening of Sparseloop architecture config.\n\n

    Arguments:\n
    - arch -- Sparseloop-format architecture object\n\n

    Returns:\n
    - Flattened architecture dictionary. Example:\n\n

    {'BackingStorage': \n
        {'attributes': \n
            {'block_size': 8, \n
             'data_storage_depth': 15000, \n
             'data_storage_width': 64, \n
             'datawidth': 8, \n
             'metadata_storage_depth': 368640, \n
             'metadata_storage_width': 14}, \n
         'class': 'storage', \n
         'subclass': 'DUMMY_SRAM_MD_BackingStorage_SAF'}, \n
     'iact_spad': ...,\n
     ...
    }
    '''
    return flatten_arch_recursive(arch['architecture']['subtree'])

def buffer_loop_binding_from_sl_arch_and_map(arch, mapping, prob_instance_rank_sizes, data_space_dict_list):
    parsed_mapping=parse_sl_mapping(mapping, prob_instance_rank_sizes, data_space_dict_list)

    buffer_hierarchy=flatten_arch_wrapper(arch)

    for buffer in buffer_hierarchy:
        buffer_hierarchy[buffer]['loops']=parsed_mapping[buffer]['loops']
        buffer_hierarchy[buffer]['data-spaces']=parsed_mapping[buffer]['data-spaces']

    return buffer_hierarchy

# Sparseopts parsing routines

def get_buffer_dataspace_to_fmt_layout_bindings_from_sparseopts(sparseopts,user_attributes={}):
    dense_fmt_iface_settings=pr_.parse_dense_fmt_iface_settings(user_attributes)

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
                if 'ranks' in buffer_dataspace_to_fmt_layout_binding[target_buffer]['representation-format'][target_data_space]:
                    for rank in buffer_dataspace_to_fmt_layout_binding[target_buffer]['representation-format'][target_data_space]['ranks']:
                        rank['dense']=False
        if 'action-optimization' in target_buffer_dict:
            buffer_dataspace_to_fmt_layout_binding[target_buffer]['action-optimization']=target_buffer_dict['action-optimization']
        if len(dense_fmt_iface_settings)>0 and target_buffer in dense_fmt_iface_settings:

            buffer_dense_fmt_iface_settings=dense_fmt_iface_settings[target_buffer]
            buffer_fmt_iface=buffer_dataspace_to_fmt_layout_binding.setdefault(target_buffer,{}).setdefault('representation-format',{})
            for dataspace in buffer_dense_fmt_iface_settings:
                if dataspace in buffer_fmt_iface:
                    error("User-specified dense format interfaces were provided for dataspace",dataspace, \
                          "which already has a sparse format specification.",also_stdout=True)
                    info("- Sparse format specification:",buffer_fmt_iface[dataspace])
                    info("Terminating.")
                    assert(False)
                dense_ranks=buffer_dense_fmt_iface_settings[dataspace]

                buffer_fmt_iface[dataspace] = \
                    {'ranks':[ \
                        {'format':'UOP','flattened-rankIDs':d_rank,'payload-word-bits':0,'dense':True} \
                        for d_rank in dense_ranks
                     ], \
                     'rank-application-order':'inner-to-outer'}

    return buffer_dataspace_to_fmt_layout_binding

def extract_dtypes(sparseopts,user_attributes):
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

#'''SAFmodel parsing routines'''
#def get_buffer_bandwidth_info(arch):
#    flat_arch = flatten_arch_wrapper(arch)
