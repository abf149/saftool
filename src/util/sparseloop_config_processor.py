import yaml

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

    for fact in product:
        if fact not in prob_coeff_list:
            data_space_rank_list.append(fact)    

    return data_space_rank_list


def data_space_rank_list_from_projection(projection, prob_coeff_list):
    """ Extract a list of ranks that project onto a data-space, from the data-space's projection expression.

    Keyword arguments:
    projection -- the data-space's projection expression
    prob_coeff_list -- a list of the constant coefficients associated with this problem
    """

    data_space_rank_list=[]
    for sum in projection:
        for product in sum:
            product_ranks=data_space_rank_list_from_product(product, prob_coeff_list)
            data_space_rank_list.extend(product_ranks)

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

def parse_sl_mapping(mapping, prob_instance_rank_sizes):
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
                parsed_mapping[buffer]['data-spaces']=list(prob_instance_rank_sizes.keys())
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

def buffer_loop_binding_from_sl_arch_and_map(arch, parsed_mapping):

    buffer_hierarchy=flatten_arch_wrapper(arch)

    for buffer in buffer_hierarchy:
        buffer_hierarchy[buffer]['loops']=parsed_mapping[buffer]['loops']
        buffer_hierarchy[buffer]['data-spaces']=parsed_mapping[buffer]['data-spaces']

    return buffer_hierarchy



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
