'''Create microarchitecture subcategories and subcategory instances'''

from util.taxonomy.designelement import Primitive, Component, Architecture

class Variable:
    def __init__(self,name,value):
        self.name=name
        self.value=value

class PrimitiveCategoryBuilder:
    design_element_type="Primitive"
    name_="PrimitiveCategory"
    attributes_=[]
    default_attributes_=[]
    ports_=[]

    def __init__(self):
        self.name_="Primitive"
        self.attributes_=[]
        self.ports_=[]

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
        - attr_type -- Primitive category attribute type ("format","net_type","int","string","any")
        - attr_default -- Primitive category attribute default value (can be "?")
        '''
        self.attributes_.append((attr_name,attr_type))
        self.default_attributes_.append((attr_name,attr_default))
        return self

    def port_in(self,port_name,port_net_type,port_fmt):
        self.ports_.append((port_name,"in",port_net_type,port_fmt))
        return self

    def port_out(self,port_name,port_net_type,port_fmt):
        self.ports_.append((port_name,"out",port_net_type,port_fmt))
        return self

#    def build():
#        return       
    


#def buildPrimitiveCategory(attributes={},ports)