'''Create microarchitecture subcategories and subcategory instances'''

from util.taxonomy.designelement import Primitive, Component, Architecture
import copy

class Variable:
    def __init__(self,name,value):
        self.name=name
        self.value=value
'''
- attributes:
  - - weight_spad
    - 0
    - iact_spad
    - 0
  category: skipping
  classtype: SAF
  id: skipping_saf
  target: weight_spad
'''

class PrimitiveCategory:

    def __init__(self):
        self.design_element_type="Primitive"
        self.name_="PrimitiveCategory"
        self.attributes_=[]
        self.attribute_vals=[]
        self.default_attributes_=[]
        self.ports_=[]

    def copy(self):
        return copy.deepcopy(self)

    def name(self,name_param):
        '''
        Category name\n\n

        Arguments:\n
        - name_param -- New Primitive cat
        '''
        self.name_=name_param
        return self

    def attribute(self,attr_name,attr_type,attr_default="?"):
        '''
        Add an attribute\n\n

        Arguments:\n
        - attr_name -- Primitive category attribute name\n
        - attr_type -- Primitive category attribute type ("fibertree","format","net_type","buffer","int","string","any","list(<type>)","list(*)",[<type>,type,...])
        - attr_default -- Primitive category attribute default value (can be "?")
        '''
        self.attributes_.append((attr_name,attr_type))
        self.default_attributes_.append((attr_name,attr_default))
        self.attribute_vals=copy.deepcopy(self.attributes_)
        return self

    def set_attribute(self,attr_name,val):
        '''
        Set an attribute\n\n

        Arguments:\n
        - attr_name -- Primitive category attribute name\n
        - val -- Updated attribute value
        '''        
        self.attribute_vals[self.attributes_.index(attr_name)]=val
        return self

    def port_in(self,port_name,port_net_type,port_fmt):
        self.ports_.append(("none",port_name,"in",port_net_type,port_fmt))
        return self

    def port_in_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        self.ports_.append((gen_type,port_name,"in",port_net_type,port_fmt,gen_metadata))
        return self

    def port_out(self,port_name,port_net_type,port_fmt):
        self.ports_.append(("explicit",port_name,"out",port_net_type,port_fmt))
        return self

    def port_out_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        self.ports_.append((gen_type,port_name,"out",port_net_type,port_fmt,gen_metadata))
        return self

    def build(self):
        pass
    
class SAFCategory(PrimitiveCategory):

    def __init__(self):
        super().__init__()
        self.target=None

    def target(self,target_str):
        self.target=target_str
        return self

class ComponentCategory(PrimitiveCategory):

    def __init__(self):
        super().__init__()
        self.topology=None

    def topological_hole(self):
        self.topology=None
        return self

class ArchitectureCategory(ComponentCategory):

    def __init__(self):
        super().__init__()
        self.topology=None
        self.buffer_hierarchy=[]
        self.saf_list=[]
        self.name_="ArchitectureCategory" # Only one architecture category

    def attribute(self):
        print("ArchitectureCategory does not support attribute()")
        assert(False)

    def port_in(self,port_name,port_net_type,port_fmt):
        print("ArchitectureCategory does not support port_in()")
        assert(False)

    def port_in_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        print("ArchitectureCategory does not support port_in_generator()")
        assert(False)

    def port_out(self,port_name,port_net_type,port_fmt):
        print("ArchitectureCategory does not support port_out()")
        assert(False)

    def port_out_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        print("ArchitectureCategory does not support port_out_generator()")
        assert(False)

    def buffers(self,buffer_list):
        self.buffer_hierarchy=buffer_list
        return self

    def buffer(self,buffer):
        self.buffer_hierarchy.append(buffer)
        return self

    def SAF(self,saf_wrapper):
        self.saf_list.append(saf_wrapper)
        return self

SAFSkipping = SAFCategory().name("skipping") \
                           .attribute("bindings",["string","int","string","int"],[None,-1,None,-1])