from util.taxonomy import expressions, serializableobject

class DesignElement(serializableobject):
    '''Elements needed to represent topologies schematically'''

    def __init__(self):
        pass

class Net(DesignElement):
    '''Nets are design elements which represent port interconnections'''

    def __init__(self):
        pass

    @classmethod
    def fromAttributes(net_type, format_type, port_list):
        '''Net from attributes: net_type (data/MD/pos), format_type (sparse repr.), list of connected port objects'''

        obj=[]
        return obj