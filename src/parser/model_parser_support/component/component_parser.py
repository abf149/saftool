'''Modelscript component parsing'''
import parser.model_parser_support.component.component_keywords as ckw_

def get_modelscript_components(script_dict):
    if ckw_.modelscript_components in script_dict:
        return script_dict[ckw_.modelscript_components]
    else:
        return []
    
def parse_modelscript_components(script_dict):
    return {}

    # Assuming that the modelscript_primitives list is not empty
    #component = script_dict[ckw_.modelscript_components][0]


    #return model_instances_dict