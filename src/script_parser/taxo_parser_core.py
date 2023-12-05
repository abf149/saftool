import script_parser.taxo_parser_support.keywords as kw_
import script_parser.taxo_parser_support.primitive.primitive_parser as prpr_
import script_parser.taxo_parser_support.component.component_parser as cmpr_
import saflib.microarchitecture.TaxoRegistry as tr_
from core.helper import info,warn,error

def parse_taxoscript(script_dict,primitives_only=False,components_only=False):
    info("-- Parsing taxoscript file.")

    # Preamble
    info("--- Taxoscript version",script_dict[kw_.taxoscript_version])
    taxoscript_primitives=prpr_.get_taxoscript_primitives(script_dict)
    taxoscript_components=cmpr_.get_taxoscript_components(script_dict)
    num_taxoscript_primitives=len(taxoscript_primitives)
    num_taxoscript_components=len(taxoscript_components)
    if primitives_only:
        num_taxoscript_components=0
    elif components_only:
        num_taxoscript_primitives=0
    num_objects=num_taxoscript_primitives+num_taxoscript_components
    info("--- Parsing",num_objects,"taxoscript objects")
    info("----",num_taxoscript_primitives,"primitives")
    info("----",num_taxoscript_components,"components")

    # Primitives
    primitives_dict={}
    if num_taxoscript_primitives>0:
        primitives_dict=prpr_.parse_taxoscript_primitives(taxoscript_primitives)
        info("---- Registering primitives (",len(list(primitives_dict.keys())),")")
        for primitive_id in primitives_dict:
            primitive_info_dict=primitives_dict[primitive_id]
            info("----- Registering",primitive_id)
            tr_.registerPrimitive(primitive_id, \
                                primitive_info_dict['primitive'], \
                                primitive_info_dict['constructor'], \
                                primitive_info_dict['instances'], \
                                primitive_info_dict['values'])
        warn("---- => Done, registering primitives")
    else:
        warn("---- => Skipping primitives")

    # Components
    components_dict={}
    if num_taxoscript_components>0:
        components_dict=cmpr_.parse_taxoscript_components(taxoscript_components)
        info("---- Registering components (",len(list(components_dict.keys())),")")
        for component_id in components_dict:
            component_info_dict=components_dict[component_id]
            info("----- Registering",component_id)
            tr_.registerComponent(component_id, \
                                component_info_dict['component'], \
                                component_info_dict['constructor'], \
                                component_info_dict['instances'], \
                                component_info_dict['topologies'], \
                                component_info_dict['values'])
        warn("---- => Done, registering components")
    else:
        warn("---- => Skipping components")

    warn("-- => Done, parsing taxoscript.")
    return primitives_dict, components_dict