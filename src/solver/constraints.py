'''Apply constraints on SAFinfer search process'''
import solver.model.build_support.abstraction as ab_
import saflib.microarchitecture.TaxoRegistry as tr_
import util.notation.predicates as pr_
from util.helper import info, warn, error
import copy

def assert_valid_force_attr_spec(force_attr_spec):
    if type(force_attr_spec).__name__ != 'list':
        error("Invalid attribute forcing settings (must be list of component component specifications)",also_stdout=True)
        info("Invalid settings:",force_attr_spec)
        info("Terminating.")
        assert(False)

def get_component_settings_list(comp_uri,force_attr_spec):
    '''
    Get attribute settings to force for specified component,
    from user-specified settings structure.
    '''
    settings_list=[]
    for spec in force_attr_spec:
        if comp_uri==spec['uri']:
            settings_list=spec['settings']
            break
    return settings_list

def assert_valid_setting(setting,comp_id):
    if ('type' not in setting) or ('values' not in setting):
        error("Invalid attribute settings for component",comp_id,also_stdout=True)
        info("Attribute settings must have type and values fields")
        info("Provided settings:",str(setting))
        info("Terminating.")
        assert(False)

def assert_valid_positional_attr_spec(attr_spec,comp_id):
    if ('position' not in attr_spec) or ('value' not in attr_spec):
        error("Invalid positional setting for component",comp_id,also_stdout=True)
        info("An individual positional attribute setting requires position and value fields.")
        info("Invalid setting:",str(attr_spec))
        info("Terminating.")
        assert(False)

def get_component_attribute_names(component):
    '''
    Get component attribute names from taxonomy registry
    '''
    category=component.getCategory()
    obj_info=None
    if pr_.isPrimitive(component):
        obj_info=tr_.getPrimitive(category)
    elif pr_.isComponent(component):
        obj_info=tr_.getComponent(category)
    else:
        assert(False)
    return [tp[0] for tp in obj_info["description"].get_attributes()]

def assert_valid_keyword_attr_spec(attr_spec,comp_id):
    if ('name' not in attr_spec) or ('value' not in attr_spec):
        error("Invalid keyword setting for component",comp_id,also_stdout=True)
        info("An individual keyword attribute setting requires name (i.e. keyword) and value fields.")
        info("Invalid setting:",str(attr_spec))
        info("Terminating.")
        assert(False)

def try_set_attribute_by_name(attr_spec,attributes_list,attr_names_list,comp_id):
    attr_name=attr_spec['name']
    attr_val=attr_spec['value']
    info("-----",str(attr_name),":",str(attr_val))
    try:
        attributes_list[attr_names_list.index(attr_name)]=attr_val
    except:
        error("Keyword",attr_name,"is not a valid attribute name for component",comp_id,also_stdout=True)
        info("Valid attribute keywords:",str(attr_names_list))
        info("Provided setting:",str(attr_spec))
        info("Terminating.")
        assert(False)

    return attributes_list

def apply_setting_to_component(component,setting):
    comp_id=component.getId()
    assert_valid_setting(setting,comp_id)
    setting_type=setting['type']
    values=setting['values']
    info("---- Setting type:",setting_type)
    if setting_type=='full':
        error("\'full\' setting type is TODO and not yet supported.",also_stdout=True)
        info("Supported setting types: positional, keyword")
        info("Context: component",comp_id)
        info("Terminating.")
        assert(False)

        component.setAttributes(values)
    elif setting_type=='positional':
        attributes_list=component.getAttributes()
        for attr_spec in values:
            assert_valid_positional_attr_spec(attr_spec,comp_id)
            info("-----",str(attr_spec['position']),":",str(attr_spec['value']))
            attributes_list[int(attr_spec['position'])]=attr_spec['value']
        component.setAttributes(attributes_list)
    elif setting_type=='keyword':
        attributes_list=component.getAttributes()
        attr_names_list=get_component_attribute_names(component)
        for attr_spec in values:
            assert_valid_keyword_attr_spec(attr_spec,comp_id)
            attributes_list=try_set_attribute_by_name \
                                (attr_spec,attributes_list,attr_names_list,comp_id)

        component.setAttributes(attributes_list)
    else:
        error(setting_type,"is not a valid setting type (full,positional,keyword).",also_stdout=True)
        info("Setting:",str(setting))
        info("Context: component",comp_id)
        info("Terminating.")
        assert(False)

    return component

def opening_remark_before_recursion(parent_uri):
    '''
    Only log at the top level of recursion tree
    '''
    if parent_uri=="":
        info("-- Checking for user-provided attributes to force.")

def closing_remark_after_recursion(parent_uri):
    '''
    Only log at the top level of recursion tree
    '''
    if parent_uri=="":
        warn("-- Done, forcing user-provided attributes")

def opening_remark_nonempty_settings_list(comp_uri,settings_list,component):
    num_settings=len(settings_list)
    if num_settings>0:
        warn("--- Forcing settings for",comp_uri,"(",str(num_settings),")")
        info("---- Initial settings:",component.getAttributes())

def closing_remark_nonempty_settings_list(comp_uri,settings_list,component):
    if len(settings_list)>0:
        info("---- Final settings:",component.getAttributes())
        warn("--- Done, forcing settings for",comp_uri)

def make_safe_uris_before_recursion(arch_id,force_attr_spec,parent_uri=""):
    if parent_uri=="":
        new_force_attr_spec=copy.copy(force_attr_spec)
        for idx,settings_spec in enumerate(new_force_attr_spec):
            uri=settings_spec['uri']
            if '/' in uri:
                info("--- Detected wildcard (\'\\\') in component uri",uri,"while parsing user-provided settings.")
                new_uri=uri.replace("/",arch_id)
                warn("---- Inferred uri:",new_uri)
                settings=settings_spec['settings']
                new_force_attr_spec[idx]={'uri':new_uri,'settings':settings}
        return new_force_attr_spec
    return force_attr_spec

def force_attributes(component,force_attr_spec,visited_set,parent_uri=""):
    '''
    Recursively force component and subcomponent attributes to match
    user-provided attribute settings.
    '''
    comp_id=component.getId()
    comp_uri=ab_.uri(parent_uri,comp_id)

    if len(force_attr_spec)==0:
        info("-- No component attributes to force.")
        return component,visited_set, force_attr_spec

    opening_remark_before_recursion(parent_uri)
    force_attr_spec=make_safe_uris_before_recursion(component.getId(),force_attr_spec,parent_uri)

    # Force attributes if this component has not already been visited
    # and this component is not a top-level architecture.
    # Mark component visited.
    if (not pr_.isArchitecture(component)) and (comp_uri not in visited_set):
        info("--- Visiting",comp_uri)
        visited_set.add(comp_uri)
        assert_valid_force_attr_spec(force_attr_spec)
        settings_list=get_component_settings_list(comp_uri,force_attr_spec)
        opening_remark_nonempty_settings_list(comp_uri,settings_list,component)
        for setting in settings_list:
            component=apply_setting_to_component(component,setting)
        closing_remark_nonempty_settings_list(comp_uri,settings_list,component)

    # Recurse and force attributes in subcomponents (unless the component is a primitive)
    if not pr_.isPrimitive(component):
        topology=component.getTopology()
        subcomponent_list=topology.getComponentList()
        new_subcomponent_list=[]
        for subcomp in subcomponent_list:
            subcomp_update,visited_set,_ = \
                force_attributes(subcomp,force_attr_spec,visited_set,parent_uri=comp_uri)

            new_subcomponent_list.append(subcomp_update)
        topology.setComponentList(new_subcomponent_list)
        component.setTopology(topology)

    closing_remark_after_recursion(parent_uri)
    return component,visited_set, force_attr_spec