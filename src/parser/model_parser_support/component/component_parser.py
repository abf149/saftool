'''Modelscript component parsing'''
import parser.model_parser_support.primitive.primitive_keywords as pkw_
#import parser.model_parser_support.primitive.primitive_syntax as ps_
import parser.model_parser_support.component.component_syntax as cs_
import parser.model_parser_support.component.component_keywords as ckw_
from util.helper import info,warn,error

def get_modelscript_components(script_dict):
    if ckw_.modelscript_components in script_dict:
        return script_dict[ckw_.modelscript_components]
    else:
        return []

def parse_modelscript_component(component):
    id_=""
    supported_instances = []
    
    # Name
    id_=cs_.parse_name(component)
    info("---- Parsing",id_)

    # Parse the from_taxonomic_component to get the instance and supported instances
    characterization_metric_models = cs_.parse_characterization_metric_models(component)
    info("")
    info("")
    model_instance, supported_instances = cs_.parse_from_taxonomic_component(component, supported_instances)
    model_instance = cs_.parse_scale_parameters(component, model_instance)
    model_instance = cs_.parse_actions(component, model_instance)
    model_instance = cs_.parse_arch_buffer_action_maps(component, model_instance)
    model_instance = cs_.register_characterization_metric_models(characterization_metric_models, model_instance)
    model_instance = cs_.parse_require_port_throughput_attributes(component, model_instance)
    model_instance = cs_.parse_export_attributes_to_model(component, model_instance)
    model_instance = cs_.parse_yield_port_throughput_thresholds(component, model_instance)
    model_instance = cs_.parse_instance_aliases(component, model_instance)
    model_instance = cs_.parse_register_supported_instances(component, model_instance, supported_instances)
    model_instance = cs_.parse_implementations(component, model_instance)
    model_instance = cs_.parse_subactions(component, model_instance)

    warn("---- => Done, parsing",id_)
    return id_,model_instance

def parse_modelscript_components(components_list):
    '''
    Arguments:\n
    - components_list -- list of modelscript component specs (mirroring the corresponding YAML)\n\n

    Returns:\n
    - components_dict[<id>] = dict["component","constructor","instances"]
    '''
    info("--- Parsing components...")
    components_dict={}
    assert(len(components_list)>0)
    for component_spec in components_list:
        id_,component = parse_modelscript_component(component_spec)
        components_dict[id_]=component
    warn("--- => Done, parsing components...")
    return components_dict