'''Basic model parsing commands'''
import parser.model_parser_support.keywords as kw_
import parser.model_parser_support.primitive.primitive_keywords as pkw_
import saflib.microarchitecture.taxo.TaxoRegistry as tr_
import util.notation.model as mo_
from util.helper import info,warn,error

def parse_name(primitive):
    return primitive[pkw_.primitive_name]

def prettystring_supported_instances(supported_instances):
    pretty_string=""
    for id_ in supported_instances:
        pretty_string+=id_ + ": " + str(supported_instances[id_]) + "\n"
    return pretty_string

def parse_from_taxonomic_primitive(primitive, supported_instances):
    #info("--- Parsing taxonomic primitive reference")
    name_ = primitive[pkw_.primitive_name]
    taxonomic_primitive = primitive[pkw_.from_taxonomic_primitive]
    taxo_primitive_dict = tr_.getPrimitive(taxonomic_primitive)
    taxo_category = taxo_primitive_dict[pkw_.taxo_primitive_description]
    taxo_category_name = taxo_category.getName()
    taxo_category_attributes = taxo_category.get_attributes()
    instances = taxo_primitive_dict[pkw_.taxo_primitive_instances]
    #nfo("---- Taxonomic category:",taxo_category_name)
    info("----",taxo_category_name,"taxonomic attributes:",taxo_category_attributes)
    model_instance = taxo_category.copy()
    info(name_,"=",taxo_category_name)
    info(".copy()")
    #supported_instances.extend(instances)
    #warn("--- => Done, parsing taxonomic primitive reference")
    return model_instance, instances

def parse_scale_parameters(primitive, model_instance):
    #info("--- Parsing scale parameters")
    for scale_param in primitive.get('scale_parameters', []):
        info(".scale_parameter(", \
             str(scale_param['name']),",", \
             str(scale_param['type']), \
            ",yield_=",str(scale_param['export_as_model_attribute']), \
            ",inherit_=",str(scale_param.get('inherit', False)),")")
        model_instance.scale_parameter(
            scale_param['name'],
            scale_param['type'],
            yield_=scale_param['export_as_model_attribute'],
            inherit_=scale_param.get('inherit', False)
        )
    #warn("--- => Done, parsing scale parameters")
    return model_instance

def parse_actions(primitive, model_instance):
    for action in primitive.get('actions', []):
        info(".action(",action['name'],")")
        model_instance.action(action['name'])
    return model_instance

def parse_load_ranks_list(sym_load_tensors_list):
    parsed_load_ranks_list=[]
    #parsed_sym_flav=kw_.parse_symbol_flavor(sym_flav)
    for sym_load_tensor_dict in sym_load_tensors_list:
        tensor_id=sym_load_tensor_dict['load_tensor']
        load_ranks_list=sym_load_tensor_dict['load_ranks']
        for load_rank_dict in load_ranks_list:
            load_rank=load_rank_dict['load_rank']
            parsed_load_rank=kw_.parse_load_rank(tensor_id,load_rank)
            parsed_load_ranks_list.append(parsed_load_rank)
    return parsed_load_ranks_list 

def parse_load_symbol_port_flavors(load_symbol):
    return load_symbol['port'],load_symbol['symbol_types']

def parse_flavor(sym_flav_dict):
    return sym_flav_dict['type']

def parse_symbol_load_tensors_list(sym_flav_dict):
    return sym_flav_dict['load_tensors']

def print_require_port_throughput_attributes(port,parsed_load_ranks_list=None):
    if parsed_load_ranks_list is None:
        info(".require_port_throughput_attributes(",str(port),")")
    else:
        info(".require_port_throughput_attributes(",str(port),",", \
                parsed_load_ranks_list,")")

def parse_require_port_throughput_attributes(primitive, model_instance):
    for load_symbol in primitive.get('load_symbols', []):
        port,symbol_flavors=parse_load_symbol_port_flavors(load_symbol)
        for sym_flav_dict in symbol_flavors:
            sym_flav=parse_flavor(sym_flav_dict)
            if sym_flav=='level':
                sym_load_tensors_list=parse_symbol_load_tensors_list(sym_flav_dict)
                if sym_load_tensors_list=='all':
                    # Require port throughput attributes for all load symbols
                    print_require_port_throughput_attributes(port)
                    model_instance.require_port_throughput_attributes(port)
                else:
                    # Require port throughput attributes for specific symbols
                    parsed_load_ranks_list=parse_load_ranks_list(sym_load_tensors_list)
                    print_require_port_throughput_attributes(port,parsed_load_ranks_list)
                    model_instance.require_port_throughput_attributes(port,parsed_load_ranks_list)
    return model_instance

def parse_export_attributes_to_model(primitive, model_instance):
    '''
    for load_symbol in primitive.get('load_symbols', []):
        port = load_symbol['port']
        symbol_flavors = load_symbol['symbol_types']
        for sym_flav_dict in symbol_flavors:
            sym_flav=sym_flav_dict['type']
            if sym_flav=='level':
    '''
    if primitive.get('export_attributes_to_model', False):
        info(".yield_taxonomic_attributes()")
        model_instance.yield_taxonomic_attributes()
    
    return model_instance

def print_yield_port_throughput_thresholds(port_attr_dict):
    #info(".yield_port_throughput_thresholds(port_attr_dict=",port_attr_dict,")")
    info(".yield_port_throughput_thresholds(port_attr_dict={")
    for port in port_attr_dict:
        info(" ",port,":",port_attr_dict[port])
    info("})")

def parse_yield_port_throughput_thresholds(primitive, model_instance):
    port_attr_dict={}
    for load_symbol in primitive.get('load_symbols', []):
        port,symbol_flavors=parse_load_symbol_port_flavors(load_symbol)
        for sym_flav_dict in symbol_flavors:
            sym_flav=parse_flavor(sym_flav_dict)
            if sym_flav=='peak':
                port_attr_dict[port]=[]
                sym_load_tensors_list=parse_symbol_load_tensors_list(sym_flav_dict)
                if sym_load_tensors_list=='all':
                    error("Implicit load tensors/load ranks not yet supported.")
                    info("Terminating.")
                    assert(False)
                    '''
                    # Require port throughput attributes for all load symbols
                    print_require_port_throughput_attributes(port)
                    model_instance.require_port_throughput_attributes(port)
                    '''
                else:
                    # Require port throughput attributes for specific symbols
                    port_attr_dict[port]=parse_load_ranks_list(sym_load_tensors_list)
                    #print_require_port_throughput_attributes(port,parsed_load_ranks_list)
                    #model_instance.require_port_throughput_attributes(port,parsed_load_ranks_list)
    '''
    port_attr_dict = {}
    for load_symbol in primitive.get('load_symbols', []):
        port = load_symbol['port']
        attributes = [list(level.keys())[0] for level in load_symbol['level']]
        port_attr_dict[port] = attributes
    '''
    print_yield_port_throughput_thresholds(port_attr_dict)
    model_instance.yield_port_throughput_thresholds(port_attr_dict=port_attr_dict)
    return model_instance

def parse_instance_aliases(primitive, model_instance):
    for instance_alias in primitive.get('instance_aliases', []):
        alias = instance_alias['alias']
        instances = instance_alias['instances']
        info(".taxonomic_instance_alias(",str(instances),",",str(alias),")")
        model_instance.taxonomic_instance_alias(instances, alias)
    return model_instance

def parse_register_supported_instances(primitive, model_instance, supported_instances):
    info(".register_supported_instances(")
    supported_instances_prettystring=prettystring_supported_instances(supported_instances)
    info(supported_instances_prettystring)
    info(")")
    model_instance.register_supported_instances(supported_instances)
    return model_instance

def parse_values_constraint(item):
    '''
    Arguments:\n
    - item -- YAML dict with symbol and values fields\n\n

    Return:\n
    - Constraint
    '''
    symbol = item['symbol']
    values = tuple(item['values'])
    sym_dict=kw_.parse_symbol(symbol)
    sym_expr="@"+sym_dict['port']+'_$a'+sym_dict['flavor']
    constraints=mo_.makeValuesConstraint(
        sym_expr,
        foralls=[("a", "attrs", [sym_dict['load_rank']])],
        ranges=[values]
    )
    return constraints

def parse_passthrough_constraint(passthru_constraint):
    '''
    Arguments:\n
    - passthru_constraint -- YAML dict with port_in, port_out and suffixes\n\n

    Return:\n
    - Constraint
    '''
    constraints_list=[]
    suffix_list=passthru_constraint['suffixes']
    port_in=passthru_constraint['port_in']
    port_out=passthru_constraint['port_out']
    for suffix_sym in suffix_list:
        suffix_sym_dict=kw_.parse_symbol(suffix_sym)
        constraints_list.append(
            mo_.makePassthroughConstraint(
                port_in+"_$a",
                port_out+"_$a",
                foralls=[("a", "attrs", [suffix_sym_dict['load_rank']])]
            )
        )
    return constraints_list



def print_implementation(name, \
                         taxonomic_instance, \
                         attr_range_specs, \
                         constraints_param, \
                         energy_objective, \
                         area_objective):
    '''Print parsed implementation'''
    info(".add_implementation(")
    info("  name =",str(name),",")
    info("  taxonomic_instance =",str(taxonomic_instance),",")
    info("  attr_range_specs = [") #,str(attr_range_specs),","
    for spec in attr_range_specs:
        info("    {")
        for k in spec:
            info("     ",k,":",spec[k],",")
        info("    },")
    info("  ],")
    info("  constraints = [")
    for const_ in constraints_param:
        info("    {")
        for k in const_:
            info("     ",k,":",const_[k],',')
        info("    },")
    info("  ],")
    #info("  energy_objective =",str(energy_objective),",")
    info("  energy_objective = {")
    for action in energy_objective:
        info("   ",action,":",energy_objective[action],',')
    info("  },")
    info("  area_objective =",str(area_objective),",")
    info(")")

def parse_implementations(primitive, model_instance):
    
    # Extract the implementations list from the primitive dictionary.
    implementations = primitive.get('implementations', [])
    
    for impl in implementations:
        name = impl['name']
        taxonomic_instance = impl['taxonomic_instance_alias']

        # Process objectives
        objectives = impl.get('objective', {})
        energy_objective = {action['name']: str(action['energy']).replace('%', '#') 
                            for action in objectives.get('actions', [])}
        area_objective = str(objectives.get('area', '')).replace('%', '#')
        
        # Process constraints
        constraints = impl.get('constraints', [])
        attr_range_specs = []
        constraints_param = []
        
        for constraint in constraints:
            if constraint['type'] == 'values':
                # Process the 'values' constraint.
                for item in constraint['list']:
                    attr_range_specs.append(parse_values_constraint(item))
            elif constraint['type'] == 'passthrough':
                passthru_constraint_list=constraint['list']
                # Process the 'passthrough' constraint.
                for passthru_constraint in passthru_constraint_list:
                    constraints_param.extend(parse_passthrough_constraint(passthru_constraint))
        
        # Call the add_implementation method on the model_instance
        print_implementation(name, \
                             taxonomic_instance, \
                             attr_range_specs, \
                             constraints_param, \
                             energy_objective, \
                             area_objective)
        model_instance.add_implementation(
            name=name,
            taxonomic_instance=taxonomic_instance,
            attr_range_specs=attr_range_specs,
            constraints=constraints_param,
            energy_objective=energy_objective,
            area_objective=area_objective
        )

    return model_instance