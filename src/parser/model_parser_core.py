import parser.model_parser_support.keywords as kw_
import parser.model_parser_support.primitive.primitive_parser as prpr_
import parser.model_parser_support.component.component_parser as cmpr_
import saflib.microarchitecture.taxo.TaxoRegistry as tr_
import util.notation.model as mo_
from util.helper import info,warn,error

def parse_modelscript(script_dict):
    info("Parsing modelscript file.")

    # Preamble
    info("- modelscript version",script_dict[kw_.modelscript_version])
    modelscript_primitives=prpr_.get_modelscript_primitives(script_dict)
    modelscript_components=cmpr_.get_modelscript_components(script_dict)
    num_modelscript_primitives=len(modelscript_primitives)
    num_modelscript_components=len(modelscript_components)
    num_objects=num_modelscript_primitives+num_modelscript_components
    info("- Parsing",num_objects,"modelscript objects")
    info("--",num_modelscript_primitives,"primitives")
    info("--",num_modelscript_components,"components")
    
    # Primitives
    primitives_dict={}
    if num_modelscript_primitives>0:
        primitives_dict=prpr_.parse_modelscript_primitives(modelscript_primitives)

    # Components
    components_dict={}
    if num_modelscript_components>0:
        components_dict=cmpr_.parse_modelscript_components(modelscript_components)

    warn("=> Done, parsing modelscript.")

    return primitives_dict, components_dict

# Example usage:
# yaml_file_path = 'path_to_yaml_file.yaml'
# model_instance = parse_modelscript_yaml(yaml_file_path)
