import parser.taxo_parser_core as tp_
import yaml
import saflib.microarchitecture.TaxoRegistry as tr_
import core.notation.model as mo_
from core.helper import info,warn,error
from core import helper

yaml_fn='saflib/microarchitecture/modelscript/SkippingUarch.modelscript.yaml'
log_fn='test_model_parser.log'

def load_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)

helper.enable_log=True
helper.log_init(log_fn)
info('starting log')

script_dict=load_yaml(yaml_fn)
primitives_dict, components_dict=tp_.parse_modelscript(script_dict)
print(primitives_dict)
print(components_dict)