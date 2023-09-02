'''Create microarchitecture subcategories and subcategory instances'''

from util.taxonomy.designelement import Primitive, Component, Architecture, Net, FormatType, \
                                        Topology, NetType, Port, SAF
from util.helper import info,warn,error
import copy

fmt_str_convert={"UOP":"U", "RLE":"R", "C":"C","B":"B"}

class TopologyWrapper:
    def __init__(self,component_list=[],net_list=[],generator_type=None,topological_hole=True):
        self.generator_type=generator_type
        self.net_class=False
        if topological_hole:
            self.topological_hole_=True
            self.component_list=[]
            self.net_list=[]
        else:
            self.topological_hole_=False
            self.component_list=component_list
            self.net_list=net_list          
        if self.generator_type is not None:
            error("Topology does not yet support generator_type")
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

    def components(self,id_component_list):
        self.topological_hole_=False
        for id,component in id_component_list:
            self.component_list.append((id,component))
        return self

    def net(self,net):
        self.topological_hole_=False
        self.net_class=False
        self.net_list.append(net)
        return self

    def nets(self,net_list_):
        self.topological_hole_=False
        self.net_list.extend(net_list_)
        return self

    def generate_topology(self,generator_type=None,generator_config_arg=None):
        if generator_type is None:
            pass
        else:
            assert(False)

    def build(self,id="TestTopology"):
        topology=[]
        if self.topological_hole_:
            topology=Topology.holeFromId(id)
        else:
            component_list=[comp.build(cid) for cid,comp in self.component_list]
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
        self.port_attribute_refs=[]
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

    def getName(self):
        return self.name_

    def attribute(self,attr_name,attr_type,attr_default="?"):
        '''
        Add an attribute\n\n

        Arguments:\n
        - attr_name -- Primitive category attribute name\n
        - attr_type -- Primitive category attribute type ("fibertree","format","net_type","buffer","int","string","any","list(<type>)","list(*)",[<type>,type,...])
        - attr_default -- Primitive category attribute default value (can be specific value, or "?")
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
        - att_type -- None==typical setter behavior, or fibertree, or rank_list
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
        elif att_type == "rank_list":
            # Assume val is a list of flattened rank formats
            self.set_attribute(attr_name,val)
        else:
            assert(False)
        return self

    def port_in(self,port_name,port_net_type,port_fmt,attr_reference=None):
        self.ports_.append((port_name,"in",port_net_type,port_fmt,attr_reference))
        return self

    def port_out(self,port_name,port_net_type,port_fmt,attr_reference=None):
        self.ports_.append((port_name,"out",port_net_type,port_fmt,attr_reference))
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
                    port_attr_ref=port[4]
                    self.ports_.append((port_name,port_dir,port_net_type,port_net_fmt,port_attr_ref))
                idx+=1
        else:
            error("Unrecognized generator type in Primitive")
            assert(False)

        return self

    def buildInterface(self,net_type_id="TestNetType",format_type_id="TestFormatType"):
        iface=[]
        for port in self.ports_:
            net_type=NetType.fromIdValue(net_type_id,port[2])
            format_type=FormatType.fromIdValue(format_type_id,port[3])
            attr_names = [attr_[0] for attr_ in self.attributes_]
            if port[4] is None:
                iface.append(Port.fromIdDirectionNetTypeFormatType(port[0], port[1], net_type, format_type))
            else:
                attr_ref_idx = attr_names.index(port[4])
                assert(attr_ref_idx >= 0)
                iface.append(Port.fromIdDirectionNetTypeFormatType(port[0], port[1], net_type, format_type, attr_ref=attr_ref_idx))

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
        saf=SAF.fromIdCategoryAttributesTarget(id, self.name_, self.attribute_vals, self.target_)
        return saf

class ComponentCategory(PrimitiveCategory):

    def __init__(self):
        super().__init__()
        self.topology_=TopologyWrapper(component_list=[],net_list=[],topological_hole=True)

    def topological_hole(self):
        self.topology_=TopologyWrapper(component_list=[],net_list=[],topological_hole=True)
        return self

    def topology(self,topology_):
        self.topology_=topology_
        return self

    def build(self,id):
        iface=self.buildInterface()
        topology=self.topology_.build()
        comp=Component.fromIdCategoryAttributesInterfaceTopology(id,self.name_,self.attribute_vals,iface,topology)
        return comp

class ArchitectureCategory(ComponentCategory):

    def __init__(self):
        super().__init__()
        self.topology_=None
        self.buffer_hierarchy=[]
        self.saf_list=[]
        self.name_="ArchitectureCategory" # Only one architecture category

    def attribute(self):
        error("ArchitectureCategory does not support attribute()")
        assert(False)

    def port_in(self,port_name,port_net_type,port_fmt):
        error("ArchitectureCategory does not support port_in()")
        assert(False)

    def port_out(self,port_name,port_net_type,port_fmt):
        error("ArchitectureCategory does not support port_out()")
        assert(False)

    def buffers(self,buffer_list):
        self.buffer_hierarchy=buffer_list
        return self

    def buffer(self,buffer):
        self.buffer_hierarchy.append(buffer)
        return self

    def SAF(self,id,saf_wrapper):
        self.saf_list.append((id,saf_wrapper))
        return self

    def SAFs(self,id_saf_wrapper_list):
        for id,saf_wrapper in id_saf_wrapper_list:
            self.saf_list.append((id,saf_wrapper))

        return self

    def buildSAFs(self):
        saf_list=[]
        idx=0
        for id,saf in self.saf_list:
            saf_list.append(saf.build(id))
            idx+=1
        return saf_list

    def build(self,id="TestArchitecture"):
        topology=self.topology_.build()
        saf_list=self.buildSAFs()
        arch=Architecture.fromIdSAFListTopologyBufferHierarchy(id,saf_list,topology,self.buffer_hierarchy)
        return arch