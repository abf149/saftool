from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *



def dictToObjByClassAttr(dictParam):
    '''Convert a dict to an object, choosing the class type by the class attribute value. Strings and ints are returned as-is'''
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
    def fromIdDirectionNetTypeFormatType(cls, id, direction, net_type, format_type):
        '''Port from id, port direction (in/out), port net_type (data/MD/pos), port format_type (sparse repr.)'''
        obj=cls.fromId(id)
        obj.setDirection(direction)
        obj.setNetType(net_type)
        obj.setFormatType(format_type)
        return obj

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
        obj.setNetList(net_list)
        obj.setComponentList(component_list)
        return obj

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

    def getPortById(self, id):
        '''Get a Port by id'''
        return [port for port in self.getInterface() if port.id==id][0]