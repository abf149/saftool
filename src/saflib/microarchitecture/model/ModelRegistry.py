from saflib.microarchitecture.model.address_primitives.PositionGenerator import PositionGeneratorModel
from saflib.microarchitecture.model.format.MetadataParser import MetadataParserModel
from saflib.microarchitecture.model.skipping.IntersectionLeaderFollower import IntersectionLeaderFollowerModel

model_dict={}

def registerModel(name_,model):
    '''
    Add a SAF microarchitecture energy/area model to registry
    '''
    global model_dict
    model_dict[name_]=model

def getModel(name_):
    '''
    Get a SAF microarchitecture energy/area model from registry
    '''
    global model_dict
    return model_dict[name_]

registerModel("PositionGeneratorModel",PositionGeneratorModel)
registerModel("MetadataParserModel",MetadataParserModel)
registerModel("IntersectionLeaderFollowerModel",IntersectionLeaderFollowerModel)