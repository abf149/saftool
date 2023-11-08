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

    # Parse the from_taxonomic_primitive to get the instance and supported instances
    characterization_metric_taxos = ps_.parse_characterization_metric_taxos(primitive)
    info("")
    info("")
    taxo_instance, supported_instances = ps_.parse_from_taxonomic_primitive(primitive, supported_instances)
    taxo_instance = ps_.parse_scale_parameters(primitive, taxo_instance)
    taxo_instance = ps_.parse_actions(primitive, taxo_instance)
    taxo_instance = ps_.register_characterization_metric_taxos(characterization_metric_taxos, taxo_instance)
    taxo_instance = ps_.parse_require_port_throughput_attributes(primitive, taxo_instance)
    taxo_instance = ps_.parse_export_attributes_to_taxo(primitive, taxo_instance)
    taxo_instance = ps_.parse_yield_port_throughput_thresholds(primitive, taxo_instance)
    taxo_instance = ps_.parse_instance_aliases(primitive, taxo_instance)
    taxo_instance = ps_.parse_register_supported_instances(primitive, taxo_instance, supported_instances)
    taxo_instance = ps_.parse_implementations(primitive, taxo_instance)

    warn("---- => Done, parsing",id_)
    return id_,taxo_instance #{"primitive":taxo_instance,"instances":supported_instances}

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