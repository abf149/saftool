'''Logical predicate primitives for SAF inference rules'''
import util.notation.generators.boolean_operators as b_

'''Type checks'''
def isComponent(obj):
    '''
    Arguments:\n
    - obj -- SAFInfer taxonomic object\n\n

    Returns:
    - True if Component
    '''
    return type(obj).__name__ == 'Component'
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
    return type(obj).__name__ == 'Primitive'

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
