'''Taxoscript component parsing'''
import parser.taxo_parser_support.primitive.primitive_keywords as pkw_
#import parser.taxo_parser_support.primitive.primitive_syntax as cs_
import parser.taxo_parser_support.primitive.primitive_syntax as ps_
import parser.taxo_parser_support.component.component_syntax as cs_
import parser.taxo_parser_support.component.component_keywords as ckw_
import saflib.microarchitecture.TaxoRegistry as tr_
from util.helper import info,warn,error

def get_taxoscript_components(script_dict):
    if ckw_.taxoscript_components in script_dict:
        return script_dict[ckw_.taxoscript_components]
    else:
        return []

def parse_taxoscript_component(component):
    id_=""
    supported_instances = []
    
    # Name
    id_=cs_.parse_name(component)
    info("---- Parsing",id_)
    info("")
    info("")
    taxo_instance,attr_dict,iter_attr,attr_vals_list_dict = \
        cs_.parse_attributes(component)
    taxo_instance=cs_.parse_ports(component,taxo_instance)
    taxo_instance,iter_spec=cs_.parse_iterator(component,taxo_instance,iter_attr)
    info("")
    supported_instances=cs_.parse_instances(component)
    info("")
    constructor=cs_.build_constructor(id_,taxo_instance,attr_dict,iter_spec)
    info("")
    topologies=cs_.parse_topologies(component,supported_instances,iter_attr)
    warn("---- => Done, parsing",id_)
    return id_,{"component":taxo_instance, \
                "instances":supported_instances, \
                "constructor":constructor, \
                "topologies":topologies,
                "values":attr_vals_list_dict}

def parse_taxoscript_components(components_list):
    '''
    Arguments:\n
    - components_list -- list of taxoscript component specs (mirroring the corresponding YAML)\n\n

    Returns:\n
    - components_dict[<id>] = dict["component","constructor","instances"]
    '''
    info("--- Parsing components...")
    components_dict={}
    assert(len(components_list)>0)
    for component_spec in components_list:
        id_,component = parse_taxoscript_component(component_spec)
        components_dict[id_]=component
    warn("--- => Done, parsing components...")
    return components_dict