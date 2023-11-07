primitive_model_dict={}
primitive_model_yields_supersets={}
primitive_model_actions={}
component_model_dict={}
component_model_yields_supersets={}
component_model_actions={}

def registerPrimitive(name_,model):
    '''
    Add a SAF microarchitecture primitive energy/area model to registry
    '''
    global primitive_model_dict
    primitive_model_dict[name_]=model
    primitive_model_yields_supersets[name_]={key_:0 for key_ in model.get_superset_yields()}
    primitive_model_actions[name_]=model.getActions()

def registerComponent(name_,model):
    '''
    Add a SAF microarchitecture component energy/area model to registry
    '''
    global component_model_dict
    component_model_dict[name_]=model
    component_model_yields_supersets[name_]={key_:0 for key_ in model.get_superset_yields()}
    component_model_actions[name_]=model.getActions()

def getPrimitive(name_):
    '''
    Get a SAF microarchitecture primitive energy/area model from registry
    '''
    global primitive_model_dict
    return primitive_model_dict[name_]

def getComponent(name_):
    '''
    Get a SAF microarchitecture component energy/area model from registry
    '''
    global component_model_dict
    return component_model_dict[name_]