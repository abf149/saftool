'''Logical predicate primitives for SAF inference rules'''
import util.notation.generators.boolean_operators as b_
import util.notation.attributes as a_

'''Type checks'''
def isComponent(obj):
    '''
    Arguments:\n
    - obj -- SAFInfer taxonomic object\n\n

    Returns:
    - True if Component
    '''
    x=type(obj).__name__ == 'Component'
    #print("isComponent:",x)
    return x
def isArchitecture(obj):
    '''
    Arguments:\n
    - obj -- SAFInfer taxonomic object\n\n

    Returns:
    - True if Architecture
    '''    
    return type(obj).__name__ == 'Architecture'
def isPrimitive(obj):
    '''
    Arguments:\n
    - obj -- SAFInfer taxonomic object\n\n

    Returns:
    - True if Primitive
    '''    
    x=type(obj).__name__ == 'Primitive'
    #print("isPrimitive:",x)
    return x
def isCategory(obj,category):
    return obj.getCategory()==category

'''Topology checks'''
def hasNets(obj):
    '''
    Arguments:\n
    - obj -- SAFInfer taxonomic object\n\n

    Returns:
    - True if object topology has >0 topological nets
    '''    
    return len(obj.getTopology().getNetList())>0
def hasTopologicalHole(obj):
    '''
    Arguments:\n
    - obj -- SAFInfer taxonomic object\n\n

    Returns:
    - True if object topology has a hole
    '''        
    return obj.getTopology().isHole()

'''Attribute checks'''
def isFormatAttribute(att):
    return type(att).__name__ == 'FormatType'
def isUnknownFormatAttribute(att):
    return b_.AND(isFormatAttribute,lambda x: x.isUnknown())(att)
def isKnownFormatAttribute(att):
    return b_.AND(isFormatAttribute,lambda x: not x.isUnknown())(att)
def hasKnownInterfaceTypeReferencingUnknownAttribute(obj):
    return a_.getKnownInterfaceTypeReferencingUnknownAttribute(obj)[0]
def hasKnownAttributeTypeReferencedByPortWithUnknownAttribute(obj):
    return a_.getKnownAttributeTypeReferencedByPortWithUnknownAttribute(obj)[0]

'''Port checks'''
def isPortWithUnknownFormat(port):
    return port.getFormatType().isUnknown()

'''Useful compound predicates'''
def isComponentOrPrimitive(obj):
    return b_.OR(isComponent,isPrimitive)(obj)
def isComponentOrArchitecture(obj):
    return b_.OR(isComponent,isArchitecture)(obj)
def isComponentOrArchitectureHasNets(obj):
    return b_.AND(b_.OR(isComponent,isArchitecture),hasNets)(obj)
def isComponentOrPrimitiveIsCategory(obj,category):
    return isComponentOrPrimitive(obj) and isCategory(obj,category)

def canFloodNetFormatToObjPorts(obj):
    net_list=obj.getTopology().getNetList()
    iface=obj.getInterface() # TODO: hack for not having a good port read/modify/write

    for port in iface:
        # Look for unknown port types on nets with known port types. 
        if port.getFormatType().isUnknown():
            # For each port of unknown type in the component interface,
            for net in net_list:
                if port.getId() in net.getPortIdList():
                    # find any connected net(s) with ports of known type
                    for connected_port_id in net.getPortIdList():
                        if not obj.getPortById(connected_port_id).getFormatType().isUnknown():
                            return True

    return False

def canFloodNetFormatToChildPorts(obj):
    net_list=obj.getTopology().getNetList()
    comp_list=obj.getTopology().getComponentList() # TODO: hack for not having a good component read/modify/write     

    for subcomponent in comp_list:
        # Examine all subcomponents.
        subcomponent_id=subcomponent.getId() 
        iface=subcomponent.getInterface() # TODO: hack for not having a good port read/modify/write       
        for port in iface:
            # Look for unknown port types on nets with known port types. 
            if port.getFormatType().isUnknown():
                # For each port of unknown type in the subcomponent interface,
                full_port_id=subcomponent_id+'.'+port.getId()
                for net in net_list:
                    if full_port_id in net.getPortIdList():
                        # find any connected net(s) with ports of known type
                        for connected_port_id in net.getPortIdList():
                            if not obj.getPortById(connected_port_id).getFormatType().isUnknown():
                                return True

        subcomponent.setInterface(iface)
    
    return False