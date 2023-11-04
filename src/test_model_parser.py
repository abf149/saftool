import parser.model_parser_core as mp_
import yaml
import saflib.microarchitecture.taxo.TaxoRegistry as tr_
import util.notation.model as mo_
from util.helper import info,warn,error
from util import helper

yaml_fn='saflib/microarchitecture/modelscript/IntersectionLeaderFollower.modelscript.yaml'
log_fn='test_model_parser.log'

def load_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)

helper.do_log=True
helper.log_init(log_fn)
info('starting log')

script_dict=load_yaml(yaml_fn)
primitives_dict, components_dict=mp_.parse_modelscript(script_dict)
print(primitives_dict)
print(components_dict)