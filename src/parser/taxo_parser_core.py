import parser.taxo_parser_support.keywords as kw_
import parser.taxo_parser_support.primitive.primitive_parser as prpr_
import parser.taxo_parser_support.component.component_parser as cmpr_
import saflib.microarchitecture.taxo.TaxoRegistry as tr_
from util.helper import info,warn,error

def parse_taxoscript(script_dict):
    info("-- Parsing taxoscript file.")

    # Preamble
    info("--- Taxoscript version",script_dict[kw_.taxoscript_version])
    taxoscript_primitives=prpr_.get_taxoscript_primitives(script_dict)
    taxoscript_components=cmpr_.get_taxoscript_components(script_dict)
    num_taxoscript_primitives=len(taxoscript_primitives)
    num_taxoscript_components=len(taxoscript_components)
    num_objects=num_taxoscript_primitives+num_taxoscript_components
    info("--- Parsing",num_objects,"taxoscript objects")
    info("----",num_taxoscript_primitives,"primitives")
    info("----",num_taxoscript_components,"components")

    # Primitives
    primitives_dict={}
    if num_taxoscript_primitives>0:
        primitives_dict=prpr_.parse_taxoscript_primitives(taxoscript_primitives)

    # Components
    components_dict={}
    if num_taxoscript_components>0:
        components_dict=cmpr_.parse_taxoscript_components(taxoscript_components)

    warn("-- => Done, parsing taxoscript.")
    return primitives_dict, components_dict