'''Taxoscript primitive parsing'''
from util.helper import info,warn,error

'''Taxoscript primitive parsing'''
import parser.taxo_parser_support.primitive.primitive_keywords as pkw_
import parser.taxo_parser_support.primitive.primitive_syntax as ps_
from util.helper import info,warn,error

def get_taxoscript_primitives(script_dict):
    if pkw_.taxoscript_primitives in script_dict:
        return script_dict[pkw_.taxoscript_primitives]
    else:
        return []

def parse_taxoscript_primitive(primitive):
    id_=""
    supported_instances = []
    
    # Name
    id_=ps_.parse_name(primitive)
    info("---- Parsing",id_)
    info("")
    info("")
    taxo_instance,attr_dict,iterator_attr=ps_.parse_attributes(primitive)
    taxo_instance=ps_.parse_ports(primitive,taxo_instance)
    taxo_instance,iter_spec=ps_.parse_iterator(primitive,taxo_instance,attr_dict,iterator_attr)
    info("")
    supported_instances=ps_.parse_instances(primitive)
    info("")
    constructor=ps_.build_constructor(id_,taxo_instance,attr_dict,iter_spec)
    warn("---- => Done, parsing",id_)
    return id_,{"primitive":taxo_instance, \
                "instances":supported_instances, \
                "constructor":constructor}

def parse_taxoscript_primitives(primitives_list):
    '''
    Arguments:\n
    - primitives_list -- list of taxoscript primitive specs (mirroring the corresponding YAML)\n\n

    Returns:\n
    - primitives_dict[<id>] = dict["primitive","constructor","instances"]
    '''
    info("--- Parsing primitives...")
    primitives_dict={}
    assert(len(primitives_list)>0)
    for primitive_spec in primitives_list:
        id_,primitive = parse_taxoscript_primitive(primitive_spec)
        primitives_dict[id_]=primitive
    warn("--- => Done, parsing primitives...")
    return primitives_dict