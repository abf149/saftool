from core.helper import info,warn,error

primitive_taxo_description_dict={}
primitive_taxo_constructor_dict={}
primitive_taxo_instances_dict={}
primitive_taxo_attribute_values_dict={}

component_taxo_description_dict={}
component_taxo_constructor_dict={}
component_taxo_instances_dict={}
component_taxo_topologies_dict={}
component_taxo_attribute_values_dict={}

def registerPrimitive(name_, \
                      taxo_primitive_description, \
                      primitive_constructor=None, \
                      primitive_instances_dict=None, \
                      attribute_values_dict=None):
    '''
    Add a SAF microarchitecture primitive taxonomic category description to registry.\n\n

    Arguments:\n
    - name_ -- string id of primitive component.\n
    - taxo_primitive_description -- structure representing the Taxonomic description of a
    microarchitecture primitive.\n
    - primitive_constructor -- function which builds an instance of the primitive.\n
    - primitive_instances_dict -- dict of supported instance flavors (constructor parameters) of the primitive.
    '''
    global primitive_taxo_description_dict
    global primitive_taxo_constructor_dict
    global primitive_taxo_instances_dict
    global primitive_taxo_attribute_values_dict
    assert((primitive_constructor is not None) and \
           (primitive_instances_dict is not None))

    primitive_taxo_description_dict[name_]=taxo_primitive_description
    primitive_taxo_constructor_dict[name_]=primitive_constructor
    primitive_taxo_instances_dict[name_]=primitive_instances_dict
    primitive_taxo_attribute_values_dict[name_]=attribute_values_dict

def registerComponent(name_, \
                      taxo_component_description, \
                      component_constructor=None, \
                      component_instances_dict=None, \
                      component_topologies_dict=None, \
                      attribute_values_dict=None):
    '''
    Add a SAF microarchitecture component taxonomic category description to registry.\n\n

    Arguments:\n
    - name_ -- string id of component.\n
    - taxo_component_description -- structure representing the Taxonomic description of a
    microarchitecture component.\n
    - component_constructor -- function which builds an instance of the component.\n
    - component_instances -- list of supported instance flavors (constructor parameters) of the component.\n
    - component_topologies -- mapping from instance ids to implementation topologies
    '''
    global component_taxo_description_dict
    global component_taxo_constructor_dict
    global component_taxo_instances_dict
    global component_taxo_topologies_dict
    global component_taxo_attribute_values_dict
    assert((component_constructor is not None) and \
           (component_instances_dict is not None) and \
           (component_topologies_dict is not None))

    component_taxo_description_dict[name_]=taxo_component_description
    component_taxo_constructor_dict[name_]=component_constructor
    component_taxo_instances_dict[name_]=component_instances_dict
    component_taxo_topologies_dict[name_]=component_topologies_dict
    component_taxo_attribute_values_dict[name_]=attribute_values_dict

def getPrimitive(name_):
    '''
    Get a SAF microarchitecture primitive taxonomic category description.\n\n

    Arguments:\n
    - name_ -- string id of primitive component.\n\n

    Returns: dict['description','constructor','instances']
    '''
    global primitive_taxo_description_dict
    global primitive_taxo_constructor_dict
    global primitive_taxo_instances_dict
    global primitive_taxo_attribute_values_dict

    if name_ not in primitive_taxo_description_dict:
        error("Cannot find taxonomic primitive",name_,also_stdout=True)
        info("Terminating.")
        assert(False)

    return {
        'description':primitive_taxo_description_dict[name_],
        'constructor':primitive_taxo_constructor_dict[name_],
        'instances':primitive_taxo_instances_dict[name_],
        'values':primitive_taxo_attribute_values_dict[name_]
    }

def getComponent(name_):
    '''
    Get a SAF microarchitecture component taxonomic category description.\n\n

    Arguments:\n
    - name_ -- string id of component.\n\n

    Returns: dict['description','constructor','instances','topologies']
    '''
    global component_taxo_description_dict
    global component_taxo_constructor_dict
    global component_taxo_instances_dict
    global component_taxo_topologies_dict
    global component_taxo_attribute_values_dict

    if name_ not in component_taxo_description_dict:
        error("Cannot find taxonomic component",name_,also_stdout=True)
        info("Terminating.")
        assert(False)

    return {
        'description':component_taxo_description_dict[name_],
        'constructor':component_taxo_constructor_dict[name_],
        'instances':component_taxo_instances_dict[name_],
        'topologies':component_taxo_topologies_dict[name_],
        'values':component_taxo_attribute_values_dict[name_]
    }

def getPrimitiveTemplatesDict():
    return primitive_taxo_description_dict

def getPrimitiveTemplateParameterDeclarationsDict():
    return primitive_taxo_attribute_values_dict

def getPrimitiveConstructorsDict():
    return primitive_taxo_constructor_dict

def getPrimitiveTemplateSpecializationsDict():
    return primitive_taxo_instances_dict

def getComponentTemplatesDict():
    return component_taxo_description_dict

def getComponentTemplateParameterDeclarationsDict():
    return component_taxo_attribute_values_dict

def getComponentConstructorsDict():
    return component_taxo_constructor_dict

def getComponentTemplateSpecializationsDict():
    return component_taxo_instances_dict