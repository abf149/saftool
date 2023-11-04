'''Modelscript primitive parsing'''
import parser.model_parser_support.primitive.primitive_keywords as pkw_
import parser.model_parser_support.primitive.primitive_syntax as ps_
from util.helper import info,warn,error

def get_modelscript_primitives(script_dict):
    if pkw_.modelscript_primitives in script_dict:
        return script_dict[pkw_.modelscript_primitives]
    else:
        return []

def parse_modelscript_primitive(primitive):
    id_=""
    supported_instances = []
    
    # Name
    id_=ps_.parse_name(primitive)
    info("---- Parsing",id_)

    # Parse the from_taxonomic_primitive to get the instance and supported instances
    characterization_metric_models = ps_.parse_characterization_metric_models(primitive)
    info("")
    info("")
    model_instance, supported_instances = ps_.parse_from_taxonomic_primitive(primitive, supported_instances)
    model_instance = ps_.parse_scale_parameters(primitive, model_instance)
    model_instance = ps_.parse_actions(primitive, model_instance)
    model_instance = ps_.register_characterization_metric_models(characterization_metric_models, model_instance)
    model_instance = ps_.parse_require_port_throughput_attributes(primitive, model_instance)
    model_instance = ps_.parse_export_attributes_to_model(primitive, model_instance)
    model_instance = ps_.parse_yield_port_throughput_thresholds(primitive, model_instance)
    model_instance = ps_.parse_instance_aliases(primitive, model_instance)
    model_instance = ps_.parse_register_supported_instances(primitive, model_instance, supported_instances)
    model_instance = ps_.parse_implementations(primitive, model_instance)

    warn("---- => Done, parsing",id_)
    return id_,model_instance #{"primitive":model_instance,"instances":supported_instances}

def parse_modelscript_primitives(primitives_list):
    '''
    Arguments:\n
    - primitives_list -- list of modelscript primitive specs (mirroring the corresponding YAML)\n\n

    Returns:\n
    - primitives_dict[<id>] = dict["primitive","constructor","instances"]
    '''
    info("--- Parsing primitives...")
    primitives_dict={}
    assert(len(primitives_list)>0)
    for primitive_spec in primitives_list:
        id_,primitive = parse_modelscript_primitive(primitive_spec)
        primitives_dict[id_]=primitive
    warn("--- => Done, parsing primitives...")
    return primitives_dict