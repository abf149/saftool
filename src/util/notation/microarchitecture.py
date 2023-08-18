'''Create microarchitecture subcategories and subcategory instances'''

from util.taxonomy.designelement import Primitive, Component, Architecture, Net, FormatType, Topology, NetType, Port, SAF
import copy

fmt_str_convert={"UOP":"U", "RLE":"R", "C":"C","B":"B"}

'''
class Variable:
    def __init__(self,name,value):
        self.name=name
        self.value=value
'''

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

'''
class NetWrapper:
    def __init__(self,fmt="",net_type="",port_list=[]):
        self.fmt=fmt
        self.net_type_=net_type
        self.port_list=port_list

    def format(self,fmt):
        self.fmt=fmt
        return self

    def net_type(self,net_type):
        self.net_type_=net_type
        return self

    def port(self,port_name):
        self.port_list.append(port_name)
        return self

    def build(self, id, net_type_name="TestNetType", format_type_name="TestFormatType"):
        net_type=NetType.fromIdValue(net_type_name,self.net_type)
        format_type=FormatType.fromIdValue(format_type_name,self.format)
        net=Net.fromIdAttributes(id, net_type, format_type, self.port_list)
        return net        
'''

class TopologyWrapper:
    def __init__(self,component_list=[],net_list=[],generator_type=None,topological_hole=True):
        self.component_list=component_list
        self.net_list=net_list
        self.generator_type=generator_type
        self.net_class=False
        if len(component_list)>0 or len(net_list) >0:
            self.topological_hole_=False
        else:
            self.topological_hole_=topological_hole
        if self.generator_type is not None:
            print("Topology does not yet support generator_type")
            assert(False)

    def topological_hole(self):
        self.topological_hole_=True
        return self

    def generator(self,generator_type):
        self.generator_type=generator_type
        return self

    def component(self,id,component):
        self.topological_hole_=False
        self.component_list.append((id,component))
        return self

    def net(self,net):
        assert(False)
        self.topological_hole_=False
        self.net_class=True
        self.net_list.append(net)
        return self

    def n_(self,net):
        self.topological_hole_=False
        self.net_class=False
        self.net_list.append(net)
        return self

    def generate_topology(self,generator_type=None,generator_config_arg=None):
        if self.generator_type is None:
            pass
        else:
            assert(False)

    def build(self,id="TestTopology"):
        topology=[]
        if self.topological_hole_:
            topology=Topology.holeFromId(id)
        else:
            component_list=[comp.build(id) for id,comp in self.component_list]
            net_list=[Net.fromIdAttributes("net" + str(id), \
                                        self.net_list[idx][0], \
                                        self.net_list[idx][1], \
                                        list(self.net_list[idx][2:])) \
                                                for idx in range(len(self.net_list)) \
                    ]

            # build topology
            topology = Topology.fromIdNetlistComponentList(id,net_list,component_list)

        return topology

class PrimitiveCategory:

    def __init__(self):
        self.design_element_type="Primitive"
        self.name_="PrimitiveCategory"
        self.attributes_=[]
        self.attribute_vals=[]
        self.default_attributes_=[]
        self.ports_=[]
        self.generator_type=None

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

    def set_attribute(self,attr_name,val,att_type=None):
        '''
        Set an attribute\n\n

        Arguments:\n
        - attr_name -- Primitive category attribute name\n
        - val -- Updated attribute value
        '''        
        if att_type is None:
            attr_names=[att[0] for att in self.attributes_]
            self.attribute_vals[attr_names.index(attr_name)]=val
        elif att_type == "fibertree":
            # - Flatten the interface formats associated with this buffer stub
            flat_rank_fmts=[]
            for dtype in val:
                flat_rank_fmts.extend([fmt_str_convert[fmt_iface['format']] for fmt_iface in val[dtype]])
            flat_rank_fmts=[FormatType.fromIdValue('format',fmt_str) for fmt_str in flat_rank_fmts]
            self.set_attribute(attr_name,flat_rank_fmts)
        else:
            assert(False)
        return self

    def port_in(self,port_name,port_net_type,port_fmt):
        self.ports_.append((port_name,"in",port_net_type,port_fmt))
        return self

    '''
    def port_in_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        self.ports_.append((gen_type,port_name,"in",port_net_type,port_fmt,gen_metadata))
        return self
    '''

    def port_out(self,port_name,port_net_type,port_fmt):
        self.ports_.append((port_name,"out",port_net_type,port_fmt))
        return self

    def generator(self,generator_type):
        self.generator_type=generator_type
        return self

    def generate_ports(self,generator_type=None,generator_config_attribute=None):
        if self.generator_type is None:
            # Ports don't contain variables and don't need to be expanded
            return self
        elif generator_type == "fibertree":
            assert(generator_config_attribute is not None)
            # generator_config_attribute is a fibertree
            ports=self.ports_
            self.ports_=[]
            idx=0
            att_names=[att[0] for att in self.attributes_]
            for fiber in self.attribute_vals[att_names.index(generator_config_attribute)]:
                # Repeat the same pattern of ports for each fiber format
                # $v = fiber format
                # $x = fiber index
                for port in ports:
                    port_name=port[0].replace("$x",str(idx))
                    port_dir=port[1]
                    port_net_type=port[2]
                    port_net_fmt=port[3].replace("$v",fiber.getValue())
                    self.ports_.append((port_name,port_dir,port_net_type,port_net_fmt))
                idx+=1
        else:
            print("Unrecognized generator type in Primitive")
            assert(False)

        return self

    '''
    def port_out_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        self.ports_.append((gen_type,port_name,"out",port_net_type,port_fmt,gen_metadata))
        return self
    '''

    def buildInterface(self,net_type_id="TestNetType",format_type_id="TestFormatType"):
        iface=[]
        for port in self.ports_:
            net_type=NetType.fromIdValue(net_type_id,port[2])
            format_type=FormatType.fromIdValue(format_type_id,port[3])  
            iface.append(Port.fromIdDirectionNetTypeFormatType(port[0], port[1], net_type, format_type))

        return iface

    def build(self, id):
        iface=self.buildInterface()
        prim=Primitive.fromIdCategoryAttributesInterface(id, \
                                                         self.name_, \
                                                         self.attribute_vals, \
                                                         iface)
        return prim
    
class SAFCategory(PrimitiveCategory):

    def __init__(self):
        super().__init__()
        self.target_=None

    def target(self,target_str):
        self.target_=target_str
        return self

    def build(self,id=None):
        if id is None:
            # Default id: Test<category name>
            id="Test"+self.name_
        print("Attribute values:",self.attribute_vals)
        saf=SAF.fromIdCategoryAttributesTarget(id, self.name_, self.attribute_vals, self.target_)
        return saf

class ComponentCategory(PrimitiveCategory):

    def __init__(self):
        super().__init__()
        self.topology_=TopologyWrapper(topological_hole=True)

    def topological_hole(self):
        self.topology_=TopologyWrapper(topological_hole=True)
        return self

    def topology(self,topology):
        self.topology_=topology
        return self

    def build(self,id):
        #comp=super().build(id)
        iface=self.buildInterface()
        topology=self.topology_.build()
        comp=Component.fromIdCategoryAttributesInterfaceTopology(id,self.name_,self.attribute_vals,iface,topology)
        return comp

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

    '''
    def port_in_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        print("ArchitectureCategory does not support port_in_generator()")
        assert(False)
    '''

    def port_out(self,port_name,port_net_type,port_fmt):
        print("ArchitectureCategory does not support port_out()")
        assert(False)

    '''
    def port_out_generator(self,port_name,port_net_type,port_fmt,gen_type="fibertree",gen_metadata="fibertree"):
        print("ArchitectureCategory does not support port_out_generator()")
        assert(False)
    '''

    def buffers(self,buffer_list):
        self.buffer_hierarchy=buffer_list
        return self

    def buffer(self,buffer):
        self.buffer_hierarchy.append(buffer)
        return self

    def SAF(self,saf_wrapper):
        self.saf_list.append(saf_wrapper)
        return self

    def buildSAFs(self):
        saf_list=[]
        idx=0
        for saf in self.saf_list:
            saf_list.append(saf.build("Test"+saf.name_+str(idx)))
            idx+=1
        return saf_list

    def build(self,id="TestArchitecture"):
        topology=self.topology_.build()
        saf_list=self.buildSAFs()
        arch=Architecture.fromIdSAFListTopologyBufferHierarchy(id,saf_list,topology,self.buffer_hierarchy)
        return arch

'''Define a baseline of SAF, primitive and component categories'''

ArchitectureBase = ArchitectureCategory()

BufferStub = PrimitiveCategory().name("BufferStub") \
                                .port_out("md_out$x","md","$v") \
                                .port_in("pos_in$x","pos","addr") \
                                .port_in("at_bound_in$x","pos","?") \
                                .attribute("fibertree",["fibertree"],[None]) \
                                .generator("fibertree")


SAFFormat = SAFCategory().name("format") \
                         .attribute("fibertree",["fibertree"],[None])

print("SAFFormat:",SAFFormat)
                         
SAFSkipping = SAFCategory().name("skipping") \
                           .attribute("bindings",["string","int","string","int"],[None,-1,None,-1])