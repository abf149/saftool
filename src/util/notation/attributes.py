from util.helper import info, warn, error

'''Nets'''
def getNetType(x,x_type="port"):
    if x_type=="port":
        return x.getNetType().getValue()
    else:
        error("Unknown x_type in getNetType()")
        assert(False)

'''Ports'''
def getFormat(x,x_type="port"):
    if x_type=="port":
        return x.getFormatType().getValue()
    else:
        error("Unknown x_type in getFormatType()")
        assert(False)

def portInObjInterface(port,obj):
    return port.getId() in [port.getId() for port in obj.getInterface()]

def portInNet(port,net):
    return port.getId() in net.getPortIdList()

'''Types and identifiers'''
def getCategory(obj):
    return obj.getCategory()

'''Interacting with the underlying serializable object representation'''
def getSerializableObjAttribute(obj, attr_name):
    return obj.toDict()[attr_name]