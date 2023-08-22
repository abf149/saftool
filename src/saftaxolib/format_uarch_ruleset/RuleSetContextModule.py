# Format uarch RuleSet

from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
import util.notation.predicates as p_
import util.notation.generators.boolean_operators as b_
import util.notation.generators.quantifiers as q_
import util.notation.generators.comparison as c_
import util.notation.attributes as a_
import util.notation.microarchitecture as m_
from saftaxolib.primitive_md_parser_ruleset.RuleSetContextModule import MetadataParser

# - Format microarchitecture

FormatUarch = m_.ComponentCategory().name("FormatUarch") \
                                    .port_in("md_in$x","md","$v") \
                                    .port_out("at_bound_out$x","pos","addr") \
                                    .attribute("fibertree",["fibertree"],[None]) \
                                    .generator("fibertree")

# - Format SAF rewrite rules

# -- ConcretizeArchitectureFormatSAFsToFormatUarches
# --- concretization rule

def formatUarchPortIdToBufferPortIdMapping(format_uarch_port_id):
    format_uarch_port_prefix_list=['md_in','at_bound_out']
    buffer_port_prefix_list=['md_out','at_bound_in']

    for format_uarch_port_prefix,buffer_port_prefix in zip(format_uarch_port_prefix_list,buffer_port_prefix_list):
        if format_uarch_port_id.startswith(format_uarch_port_prefix):
            port_idx=format_uarch_port_id.split(format_uarch_port_prefix)[1]
            buffer_port_id=buffer_port_prefix+port_idx
            return buffer_port_id

def concretizeArchitectureFormatSAFsToFormatUarches(obj):
    '''Object is an architecture with at least one format SAF; concretize format SAF(s) to format uarch(es) and critically, DELETE THE FORMAT SAFS'''
    
    arch_saf_list=obj.getSAFList()

    arch_format_saf_list=[format_saf for format_saf in arch_saf_list if format_saf.getCategory() == 'format']
    arch_non_format_saf_list=[format_saf for format_saf in arch_saf_list if format_saf.getCategory() != 'format']
    arch_format_saf_target_list=[format_saf.getTarget() for format_saf in arch_format_saf_list]
    arch_target_buffer_interface_list=[obj.getSubcomponentById(target_id).getInterface() for target_id in arch_format_saf_target_list]
    arch_format_saf_ranks_list=[format_saf.getAttributes()[0] for format_saf in arch_format_saf_list]

    arch_topology=obj.getTopology()
    arch_topology_component_list=arch_topology.getComponentList()
    arch_topology_net_list=arch_topology.getNetList()

    for idx in range(len(arch_format_saf_list)):
        # Concretize format SAF to format uarch
        buffer_id=arch_format_saf_target_list[idx]     

        format_uarch=FormatUarch.copy() \
                            .set_attribute("fibertree",arch_format_saf_ranks_list[idx],"rank_list") \
                            .generate_ports("fibertree","fibertree") \
                            .build(buffer_id+"_datatype_format_uarch")

        # Add format uarch to architecture
        arch_topology_component_list.append(format_uarch)

        # Net list setup
        format_uarch_id=format_uarch.getId()
        format_uarch_interface_list=format_uarch.getInterface()
        buffer_port_id_list=[port.getId() for port in arch_target_buffer_interface_list[idx]]

        for format_uarch_port in format_uarch_interface_list:
            format_uarch_port_id=format_uarch_port.getId()
            buffer_port_id=formatUarchPortIdToBufferPortIdMapping(format_uarch_port_id)
            assert(buffer_port_id in buffer_port_id_list) # Assert mapped buffer port exists
            format_uarch_port_id=format_uarch_id+'.'+format_uarch_port_id
            buffer_port_id=buffer_id+'.'+buffer_port_id

            net_type=format_uarch_port.getNetType()
            format_type=FormatType.fromIdValue('TestFormatType','?')
            port_id_list=[format_uarch_port_id,buffer_port_id]
            net=Net.fromIdAttributes('net_'+format_uarch_port_id+'_'+buffer_port_id, net_type, format_type, port_id_list)

            arch_topology_net_list.append(net)

    arch_topology.setComponentList(arch_topology_component_list)
    arch_topology.setNetList(arch_topology_net_list)
    obj.setTopology(arch_topology)

    # Delete format SAFs
    obj.setSAFList(arch_non_format_saf_list)

    return obj



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

