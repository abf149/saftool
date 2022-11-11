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
