import parser.taxo_parser_core as tp_
import yaml
import saflib.microarchitecture.taxo.TaxoRegistry as tr_
import util.notation.taxo as mo_
from util.helper import info,warn,error
from util import helper

yaml_fn='saflib/microarchitecture/taxoscript/SkippingUarch.taxoscript.yaml'
log_fn='test_taxo_parser.log'

def load_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)

helper.do_log=True
helper.log_init(log_fn)
info('starting log')

script_dict=load_yaml(yaml_fn)
primitives_dict, components_dict=tp_.parse_taxoscript(script_dict)
print(primitives_dict)
print(components_dict)