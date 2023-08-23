# Format uarch RuleSet
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.notation import predicates as p_, attributes as a_, microarchitecture as m_, transform as t_
from util.notation.generators import boolean_operators as b_, quantifiers as q_, comparison as c_
#from ..primitive_md_parser_ruleset.RuleSetContextModule import MetadataParser
from .microarchitecture import newFMTUarchBufferStubNetlistFromFMTSAF, MetadataParser
from .saf import isFMTSAF, FMTSAFtoUarch
from functools import reduce

''' - Format SAF rewrite rules'''
''' -- ConcretizeArchitectureFormatSAFsToFormatUarches'''
''' --- concretization rule'''
concretizeArchitectureFormatSAFsToFormatUarches = \
    lambda obj: t_.transformSAFs(
                    t_.transformTopology(obj, \
                                         map(FMTSAFtoUarch, filter(isFMTSAF,obj.getSAFList())), \
                                         reduce(lambda x,y: x+y, map( \
                                                 newFMTUarchBufferStubNetlistFromFMTSAF, \
                                                 filter(isFMTSAF,obj.getSAFList())),[]), \
                                         append=True), \
                    filter(b_.NOT(isFMTSAF),obj.getSAFList()), append=False \
                )

''' --- predicate '''
'''Object is an architecture with at least one format SAF'''
predicateIsArchitectureHasFormatSAF=b_.AND(p_.isArchitecture, \
                                           q_.anyForObjSAFs( \
                                                c_.equals( \
                                                    m_.SAFFormat.name_, \
                                                    a_.getCategory \
                                                )
                                            )
                                    )

# - Format uarch rewrite rules
# -- TransformTopologicalHoleToPerRankMdParserTopology: For a format uarch with a topological hole, fill the hole with a topology comprising one MetadataParser primitive per traversed tensor rank at this buffer level
def generateFormatUarchTopology(rank_format_strs):
   # Topology ID
    topology_id='TestTopology'

    # Component list setup
    component_list=[]
    for idx in range(len(rank_format_strs)):
        fmt_str=rank_format_strs[idx]
        component_list.append(MetadataParser.copy().set_attribute('format', \
                                               FormatType.fromIdValue('format',fmt_str)
                                              ).build('TestMetadataParser'+str(idx)))

    # Net list setup

    # - Nets connecting metadata (md) ports to primitives, position (pos) ports to primitives
    net_list=[]
    for idx in range(len(rank_format_strs)): 
        fmt_str=rank_format_strs[idx]        
        # Metadata net
        net_type=NetType.fromIdValue('TestNetType','md')
        format_type=FormatType.fromIdValue('TestFormatType',fmt_str)
        port_id_list=['md_in'+str(idx),'TestMetadataParser'+str(idx)+'.md_in']
        net_md=Net.fromIdAttributes('TestMDNet'+str(idx), net_type, format_type, port_id_list)
        # Position net
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','addr')
        port_id_list=['at_bound_out'+str(idx),'TestMetadataParser'+str(idx)+'.at_bound_out']
        net_at_bound=Net.fromIdAttributes('TestPosNet'+str(idx), net_type, format_type, port_id_list)
        net_list.append(net_md)
        net_list.append(net_at_bound)

    # build topology
    return Topology.fromIdNetlistComponentList(topology_id,net_list,component_list)

def transformTopologicalHoleToPerRankMdParserTopology(obj):
    '''Fill the topological hole with a topology comprising one MetadataParser primitive per traversed tensor rank at this buffer level'''
    rank_format_strs = [fmt_type['value'] for fmt_type in obj.attributes[0]]
    obj.setTopology(generateFormatUarchTopology(rank_format_strs))
    return obj

def predicateIsComponent(obj):
    return type(obj).__name__ == 'Component'

def predicateIsFormatUarch(obj):
    return obj.getCategory() == 'FormatUarch'

def predicateHasTopologicalHole(obj):
    return obj.getTopology().isHole()

def predicateIsComponentIsFormatUarchHasTopologicalHole(obj):
    return predicateIsComponent(obj) and predicateIsFormatUarch(obj) and predicateHasTopologicalHole(obj)

# - MetadataParser validation rules

# -- AssertPrimitiveMetadataParserSupportedInstantiation: MetadataParser instance must be supported

def assertPrimitiveMetadataParserAttributesAreSupported(obj):
    '''Assert that MetadataParser primitive instance is supported. Format must be in ['C','B'] or unknown'''
    fmt=obj.getAttributeById('format').getValue()
    return fmt in ['C','B','R','U','?']

predicateIsPrimitiveMetadataParser=b_.AND(p_.isPrimitive,c_.equals(MetadataParser.name_,a_.getCategory))

# - MetadataParser rewrite rules

def transformUnknownAttributeTypeFromInterfaceType(obj):
    attribute_unknown=obj.getAttributeById('format').isUnknown()

    interface_type=obj.getPortById('md_in').getFormatType().getValue()

    # TODO: make a real read/modify/write for attributes
    atts=obj.getAttributes()
    for idx in range(len(atts)):
        if type(atts[idx]).__name__=='FormatType' and atts[idx].getId()=='format':
            atts[idx].setValue(interface_type)
    obj.setAttributes(atts)
    return obj



def predicateIsPrimitiveMetadataParserHasUnknownAttributeTypeAndKnownInterfaceType(obj):
    return predicateIsPrimitiveMetadataParser(obj) and (not obj.getPortById('md_in').getFormatType().isUnknown()) and obj.getAttributeById('format').isUnknown()

