from util.taxonomy.designelement import Primitive, Component, Architecture, Net, FormatType, \
                                        Topology, NetType, Port, SAF
from util.helper import info,warn,error
import copy

class PrimitiveModel:

    def __init__(self):
        self.design_element_type="Primitive"
        self.name_="PrimitiveModel"
        self.attribute_map={}

    def build(self,id):
        pass