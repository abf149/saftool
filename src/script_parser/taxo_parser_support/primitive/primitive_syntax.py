'''Basic taxo primitive parsing commands'''
from core.notation import microarchitecture as m_
import core.taxonomy.designelement as de_
import script_parser.taxo_parser_support.keywords as kw_
from core.helper import info,warn,error

def parse_name(primitive):
    if kw_.object_name not in primitive:
        error("Taxonomic primitive must have \'name\' field.")
        info("Primitive:")
        info(str(primitive))
    return primitive[kw_.object_name]

def is_none(val_):
    '''
    None, 'None', or 'none' are valid None's
    '''
    return ((val_ is None) or (val_=="None") or (val_=="none"))

def standardize_if_none(val_):
    '''
    Returns non-none values unmodified; standardizes None,'None',or 'none' to None
    '''
    if is_none(val_):
        return None
    return val_

def cast_value_to_type(val_,type_,fmt_as_string=False):
    if type_==kw_.string_attr_type:
        if is_none(val_):
            return None
        return str(val_)
    elif type_==kw_.format_attr_type:
        res_str="?"
        if not is_none(val_):
            res_str=str(val_)
        if fmt_as_string:
            return res_str
        else:
            return de_.FormatType.fromIdValue("format",res_str)        
    elif type_==kw_.int_attr_type:
        if is_none(val_):
            return None
        return int(val_)
    elif type_==kw_.fibertree_attr_type:
        if is_none(val_):
            return [None]
        elif type(val_).__name__=='list':
            return val_
        else:
            error("Fibertree value",val_,"is not ranklist, None or \'None\'",also_stdout=True)
            info("Terminating.")
            assert(False)
    error("Invalid type",type_,"not one of",kw_.valid_attr_types,also_stdout=True)
    info("Terminating.")
    assert(False)

def format_type_string(type_):
    if type_==kw_.fibertree_attr_type:
        return [kw_.fibertree_attr_type]
    return type_

def get_single_dict_key(dict_):
    '''
    Takes a dict with one key, and returns the key
    '''
    return list(dict_.keys())[0]

def attribute_has_values_spec(expr_dict):
    if len(list(expr_dict.keys()))>1:
        key_test=any([k=="values" for k in expr_dict])
        if not key_test:
            error("Attribute expression",expr_dict, \
                  "has two keys but none of them are a values specification.")
            info("Terminating.")
            assert(False)
        return True
    return False

def get_attr_type_and_val_list(expr_dict):
    if attribute_has_values_spec(expr_dict):
        for k in expr_dict:
            if k!="values":
                return k,expr_dict["values"]
    return get_single_dict_key(expr_dict),None
                

def parse_attribute_expression(expr_dict):
    '''
    Parse taxoscript attribute expression.\n\n

    Arguments:\n
    - expr_dict -- {<type>:(expr str)}

    Returns
    '''
    attr_type,attr_val_list=get_attr_type_and_val_list(expr_dict)
    attr_name=expr_dict[attr_type]
    attr_default=None
    is_iterator=False

    if '^' in attr_name:
        if attr_name[0]!='^':
            error("Unexpected iterator annotation ^ in middle of attribute expression",attr_name, \
                  "; did you mean to put this at the beginning of the expression?",also_stdout=True)
            info("Terminating.")
            assert(False)
        is_iterator=True
        attr_name=attr_name[1:]

    if '=' in attr_name:
        attr_name_split=attr_name.split('=')
        attr_name=attr_name_split[0]
        attr_default=attr_name_split[1]
        
    cast_attr_default=cast_value_to_type(attr_default,attr_type)
    
    return attr_name,attr_type,cast_attr_default,is_iterator,attr_val_list

def print_name(name_):
    info("#",name_,"taxonomic category")
    info("")
    info(name_,"= PrimitiveCategory().name(",name_,")")

def print_attribute(attr_name,attr_type,attr_default,is_iterator):
    if is_iterator:
        info(".attribute(",attr_name,",",attr_type,",",attr_default,") # <== ITERATOR")
    else:
        info(".attribute(",attr_name,",",attr_type,",",attr_default,")")

def parse_attributes(primitive):
    attr_vals_list_dict={}
    taxo_instance=m_.PrimitiveCategory()
    name_=parse_name(primitive)
    full_attr_dict={}
    iterator_attr=None
    # format: format=?
    # format: format
    # md_in(md)=attributes.format
    # md_in(md)=format
    # md_in(md)
    if kw_.object_attributes in primitive:
        attributes_=primitive[kw_.object_attributes]
        print_name(name_)
        taxo_instance.name(name_)
        
        for idx,attr_dict in enumerate(attributes_):
            attr_name, \
            attr_type, \
            attr_default, \
            is_iterator, \
            attr_val_list=parse_attribute_expression(attr_dict)
            attr_vals_list_dict[attr_name]={"idx":idx,"values":attr_val_list}
            formatted_type=format_type_string(attr_type)
            full_attr_dict[attr_name]={"type":attr_type,"default":attr_default,"index":idx}
            print_attribute(attr_name,formatted_type,attr_default,is_iterator)
            taxo_instance.attribute(attr_name,formatted_type,attr_default)
            if is_iterator:
                iterator_attr=attr_name
    else:
        warn("# No attributes.")

    return taxo_instance,full_attr_dict,iterator_attr,attr_vals_list_dict

def parse_port_name_net_type(expr):
    expr_splits=expr.split("(")
    port_name=expr_splits[0]
    port_net_type=expr_splits[1].split(")")[0]
    return port_name,port_net_type

def parse_port_expression(expr_dict):
    port_dir=get_single_dict_key(expr_dict)
    if port_dir not in kw_.valid_port_dirs:
        error("Invalid port dir",port_dir,"not in",kw_.valid_port_dirs,also_stdout=True)
        info("Terminating.")
        assert(False)
    port_name_net_type=expr_dict[port_dir]
    port_default=None
    port_attr_ref=None
    if '=' in port_name_net_type:
        port_name_net_type_split=port_name_net_type.split('=')
        port_name_net_type=port_name_net_type_split[0]
        port_default_or_attr_ref=port_name_net_type_split[1]
        if '.' in port_default_or_attr_ref:
            # Port attribute reference assignment; default is None
            port_default_or_attr_ref_split=port_default_or_attr_ref.split('.')
            if port_default_or_attr_ref_split[0] != kw_.object_attributes:
                error("Invalid port assignment", \
                      port_dir, \
                      expr_dict[port_dir], \
                      "(",port_default_or_attr_ref,"prefix",port_default_or_attr_ref_split[0],"invalid)", \
                      also_stdout=True)
                info("Terminating.")
                assert(False)
            port_attr_ref=port_default_or_attr_ref_split[1]
        else:
            # Default assignment; port attribute reference is None
            port_name, \
            port_net_type=parse_port_name_net_type(port_name_net_type)
            standardize_port_default=port_default=standardize_if_none(port_default_or_attr_ref)
            cast_port_default=""
            if port_net_type==kw_.md_net_type:
                cast_port_default=cast_value_to_type(standardize_port_default,'format',fmt_as_string=True)
            else:
                cast_port_default=cast_value_to_type(standardize_port_default,'string')
            return port_name, \
                   port_dir, \
                   port_net_type, \
                   cast_port_default, \
                   port_attr_ref

    port_name, \
    port_net_type=parse_port_name_net_type(port_name_net_type)
    standardize_port_default=standardize_if_none(port_default)
    cast_port_default=""
    if port_net_type==kw_.md_net_type:
        cast_port_default=cast_value_to_type(standardize_port_default,'format',fmt_as_string=True)
    else:
        cast_port_default=cast_value_to_type(standardize_port_default,'string')

    return port_name, \
           port_dir, \
           port_net_type, \
           cast_port_default, \
           port_attr_ref

def print_port_expression(port_name,port_dir,port_net_type,port_default=None,port_attr_ref=None):
    if port_dir==kw_.port_input:
        info(".port_in(",port_name,",", \
             port_net_type,",", \
             port_default,", attr_reference =",port_attr_ref,")")
    elif port_dir==kw_.port_output:
        info(".port_out(",port_name,",", \
             port_net_type,",", \
             port_default,", attr_reference =",port_attr_ref,")")
    else:
        assert(False)

def parse_ports(primitive,taxo_instance):
    if kw_.object_ports in primitive:
        port_list=primitive[kw_.object_ports]
        for port_dict in port_list:
            port_name, \
            port_dir, \
            port_net_type, \
            port_default, \
            port_attr_ref=parse_port_expression(port_dict)
            print_port_expression(port_name,port_dir,port_net_type, \
                                  port_default,port_attr_ref)
            if port_dir==kw_.port_input:
                taxo_instance.port_in(port_name,port_net_type,port_default,attr_reference=port_attr_ref)
            else:
                taxo_instance.port_out(port_name,port_net_type,port_default,attr_reference=port_attr_ref)

    return taxo_instance

def print_iterator(iter_):
    info(".generator(",iter_,")")

def parse_iterator(primitive,taxo_instance,attr_dict,iterator_attr):
    iter_=None
    if kw_.object_iterator in primitive:
        iter_=primitive[kw_.object_iterator]
    iter_std=standardize_if_none(iter_)
    print_iterator(iter_std)
    taxo_instance.generator(iter_std)
    iter_spec={}
    if not is_none(iter_std):
        # If an iterator is employed, store iterator metadata
        if iterator_attr is None:
            error("Primitive",parse_name(primitive),"has non-None",iter_std, \
                  "iterator but no iterated attribute.",also_stdout=True)
            info("Did you forget to add ^ before the iterator attribute name?",also_stdout=True)
            info("Terminating.")
            assert(False)
        iter_spec['type']=iter_std
        iter_spec['attribute']=iterator_attr
    return taxo_instance,iter_spec

def print_instances(name_,instances):
    info("#",name_,"supported instances:")
    info("{")
    for inst_name in instances:
        info(" ",inst_name,":",instances[inst_name],",")
    info("}")

def parse_instances(primitive):
    '''
        instances:
    - uncompressed: [U]
    - coordinate_payload: [C]
    - bitmask: [B]
    - run_length_encoding: [R]
    '''
    name_=parse_name(primitive)
    if kw_.object_instances not in primitive:
        error("Primitive",name_,"must have instances spec (",kw_.object_instances,")",also_stdout=True)
        info("Terminating.")
        assert(False)
    instances_dict_list=primitive[kw_.object_instances]
    instances={get_single_dict_key(inst_dict):inst_dict[get_single_dict_key(inst_dict)] \
                    for inst_dict in instances_dict_list}
    print_instances(name_,instances)
    return instances

def print_constructor(name_,attr_dict,iter_spec):
    num_args=len(list(attr_dict.keys()))
    info("#",name_,"constructor (",str(num_args),"args)")
    info("")
    args_str=",".join(list(attr_dict.keys()))
    info("def",name_,"(",args_str,"):")
    info("  return \\")
    info(" ",name_,".copy()")
    for attr_name in attr_dict:
        fields_dict=attr_dict[attr_name]
        type_=fields_dict['type']
        idx=fields_dict['index']
        info("  .set_attribute (\'",attr_name,"\', (",type_,")",attr_name,") # arg",str(idx))
    if (iter_spec is not None) and (len(iter_spec)>0):
        iter_attr=iter_spec['attribute']
        iter_type=iter_spec['type']
        info("  .generate_ports(",iter_type,",",iter_attr,")")

def build_constructor(name_,taxo_instance,attr_dict,iter_spec):
    '''
    Higher-order function which generates a convenient
    constructor function for this taxonomic category.
    '''
    print_constructor(name_,attr_dict,iter_spec)
    num_args=len(list(attr_dict.keys()))
    def constr_(*args):
        info("++ Building",name_)
        if len(args) != num_args:
            error("++ - Invalid arg count",str(len(args)),"; expected",str(num_args))
        inst_=taxo_instance.copy()
        for attr_name in attr_dict:
            fields_dict=attr_dict[attr_name]
            type_=fields_dict['type']
            idx=fields_dict['index']
            arg_val=args[idx]
            info("++ -",str(idx),":",attr_name,"= (",type_,")",arg_val)
            inst_.set_attribute(attr_name, \
                                cast_value_to_type(arg_val,type_))
        if (iter_spec is not None) and (len(iter_spec)>0):
            iter_attr=iter_spec['attribute']
            iter_type=iter_spec['type']
            info("++ - generate_ports(",iter_attr,",",iter_type,")")
            inst_.generate_ports(iter_type,iter_attr)
        warn("++ => Done building",name_)
        return inst_
    return constr_