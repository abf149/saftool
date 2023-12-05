from core.taxonomy.serializableobject import SerializableObject
from core.taxonomy.expressions import *



def dictToObjByClassAttr(dictParam):
    '''Convert a dict to an object, choosing the class type by the class attribute value. Strings, ints and lists are returned as-is'''

    if type(dictParam).__name__=='list':
        # Recurse for lists
        return [dictToObjByClassAttr(elem) for elem in dictParam]

    if type(dictParam).__name__=='int' or type(dictParam).__name__=='str':
        return dictParam

    obj=globals()[dictParam['classtype']].fromDict(dictParam)
    return obj



def getObjAttrAsObjListByClassType(obj, attr_name):
    '''Return an object's attribute by name, converted to a list of objects'''
    yaml_obj_list=getattr(obj, attr_name)
    return [dictToObjByClassAttr(dictElement) for dictElement in yaml_obj_list]



class DesignElement(SerializableObject):
    '''Elements needed to represent topologies schematically'''

    def __init__(self):
        pass

class Port(DesignElement):
    '''Ports are design elements which represent typed component interface connections'''

    def __init__(self):
        pass

    @classmethod
    def fromIdDirectionNetTypeFormatType(cls, id, direction, net_type, format_type, attr_ref=None):
        '''Port from id, port direction (in/out), port net_type (data/MD/pos), port format_type (sparse repr.)'''
        obj=cls.fromId(id)
        obj.setDirection(direction)
        obj.setNetType(net_type)
        obj.setFormatType(format_type)
        obj.setComponentAttributeReference(attr_ref)
        return obj

    '''Taxonomic attributes'''
    def setDirection(self, direction):
        '''Set the port direction ("in"/"out") which characterizes this port'''
        self.direction=direction

    def getDirection(self):
        '''Get the port direction ("in"/"out") which characterizes this port'''
        return self.direction  

    def setNetType(self, net_type):
        '''Set the net type (data/MD/pos) which characterizes this port'''
        self.setAttrAsDict('net_type',net_type)

    def getNetType(self):
        '''Get the net type (data/MD/pos) which characterizes this port'''
        return NetType.fromDict(self.net_type)

    def setFormatType(self, format_type):
        '''Set the format type (sparse repr.) which characterizes this port'''
        self.setAttrAsDict('format_type',format_type)

    def getFormatType(self):
        '''Get the format type (sparse repr.) which characterizes this port'''
        return FormatType.fromDict(self.format_type)

    def setComponentAttributeReference(self, attribute_name):
        '''Set the name of the component attribute to which this port's format type maps'''
        if attribute_name is None:
            self.attr_ref=-1
        else:
            self.attr_ref=attribute_name

    def getComponentAttributeReference(self):
        '''Get the name of the component attribute to which this port's format type maps'''
        if self.attr_ref == -1:
            return None
        else:
            return self.attr_ref

    '''Modeling attributes'''

    def getWordwidth(self):
        '''Get the word datawidth at this port'''
        return self.wordwidth

    def setWordwidth(self,wordwidth_):
        '''Set the word datawidth at this port'''
        self.wordwidth=wordwidth_

    def getWordsPerCycle(self):
        '''Get the rate of words transiting this port'''
        return self.wordrate

    def setWordPerCycle(self,wordrate_):
        self.wordrate=wordrate_

class Net(DesignElement):
    '''Nets are design elements which represent port interconnections'''

    def __init__(self):
        pass

    @classmethod
    def fromIdAttributes(cls, id, net_type, format_type, port_id_list):
        '''Net from attributes: id, net_type (data/MD/pos), format_type (sparse repr.), list of connected port objects'''

        obj=cls.fromId(id)
        obj.setNetType(net_type)
        obj.setFormatType(format_type)
        obj.setPortIdList(port_id_list)
        return obj

    def setNetType(self, net_type):
        '''Set the net type (data/MD/pos) which characterizes this port'''
        self.setAttrAsDict('net_type',net_type)

    def getNetType(self):
        '''Get the net type (data/MD/pos) which characterizes this port'''
        return NetType.fromDict(self.net_type)

    def setFormatType(self, format_type):
        '''Set the format type (sparse repr.) which characterizes this port'''
        self.setAttrAsDict('format_type',format_type)

    def getFormatType(self):
        '''Get the format type (sparse repr.) which characterizes this port'''
        return FormatType.fromDict(self.format_type)

    def setPortIdList(self, port_id_list):
        '''Set the list of connected port ids associated with this net'''
        self.port_id_list=port_id_list

    def getPortIdList(self):
        '''Get the list of connected port ids associated with this net'''
        return self.port_id_list

class Topology(DesignElement):
    '''A configuration of DesignElement's '''

    def __init__(self):
        pass

    @classmethod
    def fromIdNetlistComponentList(cls, id, net_list, component_list):
        '''Get topology from id, topology nets, and topology components'''
        obj=cls.fromId(id)
        obj.setIsHole(False)
        obj.setNetList(net_list)
        obj.setComponentList(component_list)
        return obj

    @classmethod
    def holeFromId(cls, id):
        '''Get a topological hole from id'''
        obj=cls.fromId(id)
        obj.setIsHole(True)
        obj.setNetList([])
        obj.setComponentList([])
        return obj

    def setIsHole(self, is_hole):
        self.is_hole=is_hole

    def isHole(self):
        return self.is_hole

    def setNetList(self, net_list):
        '''Set list of topological nets'''
        self.setAttrAsDictList('net_list', net_list)

    def getNetList(self):
        '''Get list of topological nets'''
        return getObjAttrAsObjListByClassType(self, 'net_list')

    def setComponentList(self, component_list):
        '''Set list of topological components'''
        self.setAttrAsDictList('component_list', component_list)

    def getComponentList(self):
        '''Get list of topological components'''
        return getObjAttrAsObjListByClassType(self, 'component_list')

    def getComponentById(self, id):
        '''Look up a component by id'''

        return [component for component in self.getComponentList() if component.getId()==id][0]



class Component(DesignElement):
    '''A functional unit with an interface, attributes and implementation topology'''

    def __init__(self):
        pass

    @classmethod
    def fromIdCategoryAttributesInterfaceTopology(cls, id, category, attributes, interface, topology):
        '''Get component from id, component category, component attributes, interface ports, and topological implementation'''
        obj=cls.fromId(id)
        obj.setCategory(category)
        obj.setAttributes(attributes)
        obj.setInterface(interface)
        obj.setTopology(topology)
        return obj

    def setCategory(self, category):
        '''Set the component category'''
        self.category=category

    def getCategory(self):
        '''Get the component category'''
        return self.category

    def setAttributes(self, attributes):
        '''Set the component attributes list'''
        self.setAttrAsDictList('attributes', attributes)

    def getAttributes(self):
        '''Get the component attributes list'''
        return getObjAttrAsObjListByClassType(self, 'attributes')

    def setInterface(self, interface):
        '''Set the component interface ports'''
        self.setAttrAsDictList('interface', interface)

    def getInterface(self):
        '''Get the component interface ports'''
        return getObjAttrAsObjListByClassType(self, 'interface')

    def setTopology(self, topology):
        '''Set the microarchitectural topology'''
        self.setAttrAsDict('topology', topology)

    def getTopology(self):
        '''Get the microarchitectural topology'''
        return Topology.fromDict(self.topology)

    def getSubcomponentOwningPort(self, full_port_id):
        if '.' in full_port_id:
            return [subcomp for subcomp in self.getTopology().getComponentList() if subcomp.getId()==subcomp_id][0] 
        else:
            return self

    def getPortById(self, id):
        '''Look up a port in this component's interface by id; an id of the form xxx.portid causes a lookup for portid against subcomponent xxx in this component's topology'''

        if '.' in id:
            # id format is xxx.portid; Lookup portid against subcomponent xxx in the topology
            subcomp_id,portid=id.split('.')
            subcomponent=[subcomp for subcomp in self.getTopology().getComponentList() if subcomp.getId()==subcomp_id][0]  
            return [port for port in subcomponent.getInterface() if port.getId()==portid][0]
        else:
            # Look up a port in this component's interface by id
            return [port for port in self.getInterface() if port.getId()==id][0]

    def getAttributeById(self, id):
        # TODO: handle lists well
        return [att for att in self.getAttributes() if (type(att).__name__!='list') and att.getId()==id][0]

    def getSubcomponentById(self, id):
        # Return subcomponent from topology

        return self.getTopology().getComponentById(id)

    def setAttributeByIndex(self, value, idx):
        # Set component attribute at specified index
        attrs=self.getAttributes()
        attrs[idx]=value
        self.setAttributes(attrs)

    def getAttributeByIndex(self, idx):
        return self.getAttributes()[idx]

class Primitive(Component):
    '''A "black box" functional unit with no lower-level topology; from a microarchitectural synthesis perspective, a primitive is a terminal'''

    def __init__(self):
        pass

    @classmethod
    def fromIdCategoryAttributesInterface(cls, id, category, attributes, interface):
        '''Get primitive from id, component category, component attributes, and interface ports'''
        obj=cls.fromId(id)
        obj.setCategory(category)
        obj.setAttributes(attributes)
        obj.setInterface(interface)
        return obj

class SAF(Component):
    '''Representation of an architecture-level sparse acceleration feature (SAF) specification'''

    def __init__(self):
        pass

    @classmethod
    def fromIdCategoryAttributesTarget(cls, id, category, attributes, target):
        '''Get SAF from id, SAF category, SAF attributes, and target architectural buffer (described hierarchically as a.b.c.....y.z'''
        obj=cls.fromId(id)
        obj.setCategory(category)
        obj.setAttributes(attributes)
        obj.setTarget(target)

        return obj

    def setTarget(self, target):
        self.target=target

    def getTarget(self):
        return self.target

class Architecture(Component):
    '''Skeletal representation of an accelerator architecture for the purpose of defining shared FU interfaces for microarchitecture inference'''

    def __init__(self):
        pass

    @classmethod
    def fromIdSAFListTopologyBufferHierarchy(cls, id, saf_list, topology, buffer_hierarchy):
        '''Get architecture from id, SAF list, architecture topology consisting of buffer stubs, and a list of buffer names sorted from top- to bottom-of-hierarchy'''
        obj=cls.fromIdCategoryAttributesInterfaceTopology(id, 'Architecture', [], [], topology)
        obj.setSAFList(saf_list)
        obj.setBufferHierarchy(buffer_hierarchy)
        return obj

    def setSAFList(self, saf_list):
        self.setAttrAsDictList('saf_list', saf_list)

    def getSAFList(self):
        return getObjAttrAsObjListByClassType(self, 'saf_list')

    def setBufferHierarchy(self, buffer_hierarchy):
        self.buffer_hierarchy = buffer_hierarchy

    def getBufferHierarchy(self):
        return self.buffer_hierarchy

    