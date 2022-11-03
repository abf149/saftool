import random

def genHash():
    return str(random.getrandbits(128))



class MetadataParserPrimitive:
    '''
    Represents a metadata parser primitive at the taxonomic level
    
    ...

    Attributes
    ----------
    format
        The representation format of metadata traversed by this unit
    '''

    def __init__(self,format):
        self.format=format
        self.name=genHash()
        self.genObject()

    def genObject(self):
        self.obj={}


    def getObject(self):
        return self.obj

class Formatuarch:
    '''
    Represents a Format uarch at the taxonomic level
    
    ...

    Attributes
    ----------
    fiber_subtree_rank_formats
        The fibertree representation of the subset of the fibertree iterated at this buffer level
    '''

    def __init__(self,fiber_subtree_rank_formats):
        self.name=genHash()
        self.fiber_subtree_rank_formats=fiber_subtree_rank_formats
        self.flattenUOP()

    def flattenUOP(self):
        if self.fiber_subtree_rank_formats[0] != "UOP":
            self.num_flattened_uop = 0
            self.flattened_fiber_subtree_rank_formats=self.fiber_subtree_rank_formats.copy()
            return
        
        self.flattened_fiber_subtree_rank_formats=["UOP"]

        idx=0
        while self.fiber_subtree_rank_formats[idx] != "UOP":
            idx += 1
        self.num_flattened_uop = idx
        self.flattened_fiber_subtree_rank_formats.append(self.fiber_subtree_rank_formats[idx:].copy())
        return

def calcFibertreePrefix(upper_lvl_fibertree, lower_lvl_fibertree):
    prefix_len = len(upper_lvl_fibertree) - len(lower_lvl_fibertree)
    return upper_lvl_fibertree[0:prefix_len]

def genFormatUarches(safspec):
    dataspace_arch_map = safspec.getDataspaceArchMap()
    dataspaces = dataspace_arch_map.keys()
    arch_lvls = safspec.getArchLevels()
    format_uarches = {arch_lvl:[] for arch_lvl in arch_lvls}

    for dataspace in dataspaces:
        dataspace_arch_lvls = dataspace_arch_map[dataspace]

        for arch_lvl_pair in zip(dataspace_arch_lvls,dataspace_arch_lvls[1:]):
            # Iterate pairs of consecutive architectural levels associated with this datatype
            fiber_subtree_rank_formats = calcFibertreePrefix(arch_lvl_pair[0], arch_lvl_pair[1])
            format_uarches[arch_lvl_pair[0]].append({'dataspace':dataspace, 'format_uarch':Formatuarch(fiber_subtree_rank_formats)})

    return format_uarches