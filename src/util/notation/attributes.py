from util.helper import info, warn, error
import util.notation.predicates as p_

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

def getKnownInterfaceTypeReferencingUnknownAttribute(obj):
    #print("Object ID:",obj.getId())
    for attr_idx,attr_val in enumerate(obj.getAttributes()):
        #print("attr_idx,attr_val:",attr_idx,attr_val)
        if p_.isUnknownFormatAttribute(attr_val):
            #print("unknown:",attr_idx,attr_val)
            # Find unknown attribute
            for port in obj.getInterface():
                #print("port:",port)
                if (not p_.isPortWithUnknownFormat(port)) and \
                   port.getComponentAttributeReference() == attr_idx:

                   #print("-> Found port")

                   # Find port with known format and attribute-reference
                   # to the particular unknown attribute
                   port_fmt=port.getFormatType()
                   return (True, port_fmt, attr_idx)

    return (False,None,None)


'''Interacting with the underlying serializable object representation'''
def getSerializableObjAttribute(obj, attr_name):
    return obj.toDict()[attr_name]