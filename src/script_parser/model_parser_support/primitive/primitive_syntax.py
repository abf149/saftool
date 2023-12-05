'''Basic model parsing commands'''
import script_parser.model_parser_support.keywords as kw_
import script_parser.model_parser_support.primitive.primitive_keywords as pkw_
import saflib.microarchitecture.TaxoRegistry as tr_
import core.notation.model as mo_
import core.notation.characterization as ch_
import saflib.resources.char.ResourceRegistry as rr_
from core.helper import info,warn,error
import re

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
    info("# ",taxo_category_name,"taxonomic attributes:",taxo_category_attributes)
    info("")
    model_instance = taxo_category.copy()
    info(name_,"=",taxo_category_name)
    info(".copy()")
    #supported_instances.extend(instances)
    #warn("--- => Done, parsing taxonomic primitive reference")
    return model_instance, instances

def parse_scale_parameters(primitive, model_instance):
    #info("--- Parsing scale parameters")
    has_area_multiplier=False
    for scale_param in primitive.get('scale_parameters', []):
        if scale_param['name']=='area_multiplier':
            has_area_multiplier=True
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

    if not has_area_multiplier:
        scale_param_name='area_multiplier'
        scale_param_type='real'
        scale_param_export_as_model_attribute=True
        scale_param_inherit=True
        info("")
        info("# Synthetic area_multiplier scale parameter")
        info(".scale_parameter(", \
             str(scale_param_name),",", \
             str(scale_param_type), \
            ",yield_=",str(scale_param_export_as_model_attribute), \
            ",inherit_=",str(scale_param_inherit),")")
        model_instance.scale_parameter(
            scale_param_name,
            scale_param_type,
            yield_=scale_param_export_as_model_attribute,
            inherit_=scale_param_inherit,
            param_default=1.0
        )

    #warn("--- => Done, parsing scale parameters")
    return model_instance

def parse_actions(primitive, model_instance):
    for action in primitive.get('actions', []):
        info(".action(",action['name'],")")
        model_instance.action(action['name'])
    return model_instance

'''Characterization Metric Model (chmm) parsing routines'''
def parse_chmm_name_table_id_rtl_id_expression(chmm_spec):
    return chmm_spec['name'], \
           chmm_spec['table_id'], \
           chmm_spec['rtl_id_expression']

def parse_chmm_symbol_map(chmm_spec):
    spec_list=chmm_spec['symbol_map']
    return {spec['variable']: \
                kw_.build_internal_symbol_from_syntactic_symbol(spec['symbol']) \
                    for spec in spec_list}

def parse_chmm_energy_area_latency(chmm_spec):
    # TODO: support factory methods for having multiple energy, area, latency terms
    # TODO: support more flexibility around latency

    '''
    return_list=[chmm_spec['energy'][0]['expression'], \
                 chmm_spec['energy'][0]['type'], \
                 chmm_spec['area'][0]['expression'], \
                 chmm_spec['area'][0]['type']]
    '''
    # Parse latency
    latency_range_type="" # expr: range expression, const: value, param: scale parameter value by id
    latency_expr_type="" # expr: latency independent variable expression, column_arg: specify a single column
    single_latency=False # True: final energy/area expressions are latency-independent, False: parameterized by latency
    supported_configs={("param","column_arg",True):"latencyParameterId_True_Yes", \
                       ("param","expr",False):"latencyParameterId_False_None__latencyIndependentVariableExpression", \
                       ("const","column_arg",True):"latencyConstantValue_True_Yes", \
                       ("const","expr",False):"latencyConstantValue_False_None__latencyIndependentVariableExpression", \
                       ("expr","expr",False):"latencyRangeExpression__latencyIndependentVariableExpression"}
    latency_spec=chmm_spec['latency']
    latency_dict={}

    # Categorize constraints on latency range
    # imposed by modelscript
    if 'parameter_id' in latency_spec:
        latency_range_type="param"
        latency_dict["parameter_id"]=latency_spec['parameter_id']
    elif 'constant_value' in latency_spec:
        latency_range_type="const"
        latency_dict["constant_value"]=latency_spec['constant_value']
    elif 'range_expression' in latency_spec:
        latency_range_type="expr"
        latency_dict['range_expression']=latency_spec['range_expression']

    # Categorize the way in which 'latency' synthetic column
    # is synthesized from characterization table columns
    if 'synthetic_latency_expression' in latency_spec:
        latency_expr_type="expr"
        latency_dict['synthetic_latency_expression']=latency_spec['synthetic_latency_expression']
    elif 'latency_column_name' in latency_spec:
        latency_expr_type="column_arg"
        latency_dict['latency_column_name']=latency_spec['latency_column_name']

    # parse single_latency
    if 'single_latency' in latency_spec:
        single_latency=bool(latency_spec['single_latency'])
        latency_dict['single_latency']=single_latency

    config_=(latency_range_type,latency_expr_type,single_latency)
    if config_ not in supported_configs:
        error("Latency spec latency_range_type =",str(latency_range_type), \
              "latency_expr_type =",str(latency_expr_type), \
              "single_latency =",str(single_latency),also_stdout=True)
        info("Terminating.")
        assert(False)

    latency_dict["config"]=supported_configs[config_]

    return chmm_spec['energy'][0]['expression'], \
           chmm_spec['energy'][0]['type'], \
           chmm_spec['area'][0]['expression'], \
           chmm_spec['area'][0]['type'], \
           latency_dict

def parse_chmm_approximation(chmm_spec):
    return chmm_spec['approximation']

def parse_chmm_generate_constraints(chmm_spec):
    return chmm_spec['generate_constraints']

def register_characterization_metric_models(characterization_metric_models, model_instance):
    for chmm_id in characterization_metric_models:
        chmm=characterization_metric_models[chmm_id]
        info(".register_characterization_metrics_model(<chmm_id =",chmm_id,">)")
        model_instance.register_characterization_metrics_model(chmm)
    return model_instance


def apply_latency_config_to_chmm(latency_dict,chmm):
    config_=latency_dict["config"]
    if config_=="latencyParameterId_True_Yes":
        parameter_id=latency_dict["parameter_id"]
        clock_latency_column=latency_dict["latency_column_name"]
        single_latency=True
        info(".latencyParameterId(",parameter_id,",","single_latency =", \
             single_latency,",","clock_latency_column =",clock_latency_column,")")
        chmm.latencyParameterId(parameter_id,single_latency=single_latency,clock_latency_column=clock_latency_column)
    elif config_=="latencyParameterId_False_None__latencyIndependentVariableExpression":
        parameter_id=latency_dict["parameter_id"]
        single_latency=False
        info(".latencyParameterId(",parameter_id,",","single_latency =", \
             single_latency,")")
        chmm.latencyParameterId(parameter_id,single_latency=single_latency)
        synthetic_latency_expression=latency_dict["synthetic_latency_expression"]
        info(".latencyIndependentVariableExpression(",synthetic_latency_expression,")")
        chmm.latencyIndependentVariableExpression(synthetic_latency_expression)
    elif config_=="latencyConstantValue_True_Yes":
        error("Not yet implemented.",also_stdout=True)
        info("Terminating.")
        assert(False)
    elif config_=="latencyConstantValue_False_None__latencyIndependentVariableExpression":
        error("Not yet implemented.",also_stdout=True)
        info("Terminating.")
        assert(False)
    elif config_=="latencyRangeExpression__latencyIndependentVariableExpression":
        error("Not yet implemented.",also_stdout=True)
        info("Terminating.")
        assert(False)
    return chmm

def apply_energy_config_to_chmm(expr,energy_type,chmm):
    if energy_type=="energy":
        info(".rowEnergyMetricExpression(",expr,")")
        chmm.rowEnergyMetricExpression(expr)
    elif energy_type=="power":
        info(".rowEnergyMetricFromRowPowerMetricExpression(",expr,")")
        chmm.rowEnergyMetricFromRowPowerMetricExpression(expr)
    else:
        error("Invalid energy expression type",energy_type,also_stdout=True)
        info("Terminating.")
        assert(False)
    return chmm

def apply_area_config_to_chmm(expr,area_type,chmm):
    if area_type=="area":
        info(".rowAreaMetricExpression(",expr,")")
        chmm.rowAreaMetricExpression(expr)
    else:
        error("Invalid area expression type",area_type,also_stdout=True)
        info("Terminating.")
        assert(False)
    return chmm

def parse_rtl_id_expression_variable_ids(expression):
    '''i.e. asdf$(u)lkiujh$(v) should return ['u','v']'''
    pattern = r'\$\((.*?)\)'
    matches = re.findall(pattern, expression)
    return matches

def check_variables_list_matches_symbol_map(variable_list,symbol_map):
    '''variable_list must be a subset of symbol_map keys'''
    for var_id in variable_list:
        if var_id not in symbol_map:
            error("Variable =",var_id,"not found in symbol_map =",symbol_map,also_stdout=True)
            info("Terminating.")
            assert(False)

def parse_characterization_metric_models(primitive):
    '''Parse characterization metric models'''
    ctbl_dict={}
    chmm_dict={}
    for chmm_spec in primitive.get('characterization_metric_models', []):
        # Parse
        # TODO: approximation,generate_constraints are unused
        name_, \
        table_id, \
        rtl_id_expression = parse_chmm_name_table_id_rtl_id_expression(chmm_spec)
        variables_list = parse_rtl_id_expression_variable_ids(rtl_id_expression)
        approximation = parse_chmm_approximation(chmm_spec)
        symbol_map = parse_chmm_symbol_map(chmm_spec)
        check_variables_list_matches_symbol_map(variables_list,symbol_map)
        generate_constraints = parse_chmm_generate_constraints(chmm_spec)
        energy, \
        energy_type, \
        area, \
        area_type, \
        latency_dict = parse_chmm_energy_area_latency(chmm_spec)

        #print(energy)
        #print(energy_type)
        #print(area)
        #print(area_type)
        #print(latency_dict)

        # Table
        if table_id not in ctbl_dict:
            #info("characterization_table=rr_.getCharacterizationTable(",table_id,")")
            ctbl_dict[table_id]=rr_.getCharacterizationTable(table_id)
        ctbl=ctbl_dict[table_id]

        # Characterization metric model
        info("<chmm id =",name_,">=CharacterizationMetricModel(")
        info(" ",name_,",", \
             "characterization_table=rr_.getCharacterizationTable(",table_id,"))")
        info(")")
        info(".nameExpression(",rtl_id_expression,",",variables_list,")")
        info(".symbolMap(",symbol_map,")")
        chmm=ch_.CharacterizationMetricModel(name_,ctbl) \
                .nameExpression(rtl_id_expression,variables_list) \
                .symbolMap(symbol_map)
        chmm=apply_latency_config_to_chmm(latency_dict,chmm)
        chmm=apply_energy_config_to_chmm(energy,energy_type,chmm)
        chmm=apply_area_config_to_chmm(area,area_type,chmm)
        chmm_dict[name_]=chmm
    return chmm_dict

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
    sym_expr=kw_.build_internal_symbol_from_parsed_syntactic_symbol(sym_dict,load_rank_placeholder='$a')
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
                         constraints_from_characterization_models, \
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
    chmm_const_str=""
    for const_ in constraints_from_characterization_models:
        chmm_const_str+=const_+","
    info("  constraints_from_characterization_models = [",chmm_const_str,"]")
    info("  energy_objective = {")
    for action in energy_objective:
        info("   ",action,":",energy_objective[action],',')
    info("  },")
    info("  area_objective =",str(area_objective),",")
    info(")")

def parse_custom_constraint(expr):
    return mo_.makeConstraint(expr)

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
        constraints_from_characterization_models = []
        
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
            elif constraint['type'] == 'characterization_metrics_model':
                chmm_id_list=constraint['list']
                # Process characterization metric model constraints
                for chmm_id in chmm_id_list:
                    constraints_from_characterization_models.append(chmm_id)
            elif constraint['type'] == 'custom':
                expr_list = constraint['list']
                for expr in expr_list:
                    constraints_param.append(parse_custom_constraint(expr))
        
        # Call the add_implementation method on the model_instance
        print_implementation(name, \
                             taxonomic_instance, \
                             attr_range_specs, \
                             constraints_param, \
                             constraints_from_characterization_models, \
                             energy_objective, \
                             area_objective)
        model_instance.add_implementation(
            name=name,
            taxonomic_instance=taxonomic_instance,
            attr_range_specs=attr_range_specs,
            constraints=constraints_param,
            constraints_from_characterization_models=constraints_from_characterization_models,
            energy_objective=energy_objective,
            area_objective=area_objective
        )

    return model_instance