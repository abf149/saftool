'''Modelscript keywords'''
modelscript_version='modelscript_version'
scale_parameter_name='name'

'''Symbol flavor mapping'''
symbol_flavor_map={
    'level':'',
    'peak':'_thresh'
}
def parse_symbol_flavor(flavor):
    global symbol_flavor_map
    return symbol_flavor_map[flavor]

'''Load rank notation mappings'''
datatype_load_rank_map={'metadata_word_width':'ww'}
coordinate_load_rank_map={
    'nodes_per_cycle':'cr',
    'dense_data_rank_size':'nc'
}
position_load_rank_map={
    'positions_per_cycle':'pr',
    'position_word_width':'pw'
}
bandwidth_load_rank_map={'metadata_read_width':'rw'}
load_rank_map={
    "datatype":datatype_load_rank_map,
    "coordinate":coordinate_load_rank_map,
    "position":position_load_rank_map,
    "bandwidth":bandwidth_load_rank_map
}
def parse_load_rank(tensor_id,load_rank):
    global load_rank_map
    return load_rank_map[tensor_id][load_rank]

'''Parse symbol'''
symbol_field_idx_to_name_map={
    -1:'load_rank',
    -2:'tensor_id',
    -3:'flavor',
    -4:'port'
}
def parse_symbol(symbol_str):
    '''
    Arguments:\n
    - symbol_str -- symbol expression within the modelscript syntax\n\n

    Symbol expression structure: [port].[flavor].tensor_id.load_rank\n\n

    i.e., every symbol expression must have at least tensor_id.load_rank, plus
    optionally the other fields in the above prescribed order from right
    to left.

    return:\n
    - sym_fields['port','flavor','tensor_id','load_rank']=str
    '''
    sym_splits=symbol_str.split('.')
    sym_fields={}
    num_sym_fields=len(sym_splits)
    for idx in range(num_sym_fields):
        jdx=-1-idx
        field_name=symbol_field_idx_to_name_map[jdx]
        field_value=sym_splits[jdx]
        if field_name=='tensor_id':
            tensor_id=field_value
            load_rank=sym_fields['load_rank']
            load_rank_parsed=parse_load_rank(tensor_id,load_rank)
            sym_fields['load_rank']=load_rank_parsed
        if field_name=='flavor':
            field_value=parse_symbol_flavor(field_value)

        sym_fields[field_name]=field_value
    return sym_fields

def build_internal_symbol_from_parsed_syntactic_symbol(parsed_sym_dict,load_rank_placeholder=None):
    #sym_dict=kw_.parse_symbol(symbol)
    if load_rank_placeholder is None:
        return "@"+parsed_sym_dict['port']+'_'+parsed_sym_dict['load_rank']+parsed_sym_dict['flavor']
    else:
        return "@"+parsed_sym_dict['port']+'_'+load_rank_placeholder+parsed_sym_dict['flavor']

def build_internal_symbol_from_syntactic_symbol(symbol,load_rank_placeholder=None):
    sym_dict=parse_symbol(symbol)
    return build_internal_symbol_from_parsed_syntactic_symbol(sym_dict,load_rank_placeholder)