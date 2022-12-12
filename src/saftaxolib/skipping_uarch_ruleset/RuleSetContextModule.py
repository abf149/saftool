# Skipping uarch RuleSet

from util.taxonomy.expressions import *
from util.taxonomy.designelement import *

# - Skipping SAF rewrite rules

# -- ConcretizeArchitectureSkippingSAFsToSkippingUarches
# --- concretization rule

def genSkippingUarchWithHole(skipping_uarch_id):
    '''Helper function for incomplete skipping uarch. Generate an example skipping uarch with either a topological hole, or a mix of unknown port and attribute types'''

    # Category
    component_category='SkippingUarch'

    # Attributes
    #rank_format_list=[FormatType.fromIdValue('format','C'),FormatType.fromIdValue('format','B')]
    component_attributes=['leader-follower']

    # Interface
    component_interface=[]

    # Leader/left interface
    md_format_type=FormatType.fromIdValue('TestFormatType','?') 
    pos_format_type=FormatType.fromIdValue('TestFormatType','addr')

    # -- md_in port
    net_type=NetType.fromIdValue('TestNetType','md')
    port_md_in0=Port.fromIdDirectionNetTypeFormatType('md_in0', 'in', net_type, md_format_type)

    # -- pos_out port
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')
    port_pos_out0=Port.fromIdDirectionNetTypeFormatType('pos_out0', 'out', net_type, pos_format_type)   

    # Follower/right interface
    md_format_type=FormatType.fromIdValue('TestFormatType','?') 
    pos_format_type=FormatType.fromIdValue('TestFormatType','addr')

    # -- md_in port
    net_type=NetType.fromIdValue('TestNetType','md')
    port_md_in1=Port.fromIdDirectionNetTypeFormatType('md_in1', 'in', net_type, md_format_type)

    # -- pos_out port
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')
    port_pos_out1=Port.fromIdDirectionNetTypeFormatType('pos_out1', 'out', net_type, pos_format_type)       

    component_interface.append(port_md_in0)
    component_interface.append(port_pos_out0)
    component_interface.append(port_md_in1)
    component_interface.append(port_pos_out1)    

    # Create topological hole
    component_topology=[]
    topology_id='TestTopologyHole'
    component_topology=Topology.holeFromId(id)

    # build component
    component=Component.fromIdCategoryAttributesInterfaceTopology(skipping_uarch_id,component_category,component_attributes,component_interface,component_topology)

    return component

'''
def formatUarchPortIdToBufferPortIdMapping(format_uarch_port_id):
    format_uarch_port_prefix_list=['md_in','at_bound_out']
    buffer_port_prefix_list=['md_out','at_bound_in']

    for format_uarch_port_prefix,buffer_port_prefix in zip(format_uarch_port_prefix_list,buffer_port_prefix_list):
        if format_uarch_port_id.startswith(format_uarch_port_prefix):
            port_idx=format_uarch_port_id.split(format_uarch_port_prefix)[1]
            buffer_port_id=buffer_port_prefix+port_idx
            return buffer_port_id
'''

def concretizeArchitectureSkippingSAFsToFormatUarches(obj):
    '''Object is an architecture with at least one skipping SAF; concretize skipping SAF(s) to skipping uarch(es) and critically, DELETE THE SKIPPING SAFS'''
    
    arch_saf_list=obj.getSAFList()

    arch_skipping_saf_list=[skipping_saf for skipping_saf in arch_saf_list if skipping_saf.getCategory() == 'skipping']
    arch_non_skipping_saf_list=[skipping_saf for skipping_saf in arch_saf_list if skipping_saf.getCategory() != 'skipping']

    arch_topology=obj.getTopology()
    arch_topology_component_list=arch_topology.getComponentList()
    arch_topology_net_list=arch_topology.getNetList()

    for skipping_saf in arch_skipping_saf_list:
        attrib=skipping_saf.attributes[0]

        # Unpack SAF attributes
        skipping_uarch_id='SkippingUarch'+target_buffer+str(target_port_suffix)+condition_buffer+str(condition_port_suffix)
        target_buffer=attrib[0]
        target_port_suffix=attrib[1]
        skipping_uarch_follower_right_md_in_port=skipping_uarch_id+'.md_in'+str(target_port_suffix)
        skipping_uarch_follower_right_pos_out_port=skipping_uarch_id+'.pos_out'+str(target_port_suffix)        
        condition_buffer=attrib[2]
        condition_port_suffix=attrib[3]
        skipping_uarch_leader_left_md_in_port=skipping_uarch_id+'.md_in'+str(condition_port_suffix)
        skipping_uarch_leader_left_pos_out_port=skipping_uarch_id+'.pos_out'+str(condition_port_suffix)        

        # Generate skipping uarch        
        skipping_uarch=genSkippingUarchWithHole(skipping_uarch_id)

        # Add skipping uarch to architecture
        arch_topology_component_list.append(skipping_uarch) 

        # Left/leader metadata net       
        net_type=NetType.fromIdValue('TestFormatType','md')
        format_type=FormatType.fromIdValue('TestFormatType','?')
        port_id_list=[skipping_uarch_leader_left_md_in_port,buffer_port_id]
        net=Net.fromIdAttributes('net_'+format_uarch_port_id+'_'+buffer_port_id, net_type, format_type, port_id_list)

        arch_topology_net_list.append(net)

    arch_format_saf_target_list=[format_saf.getTarget() for format_saf in arch_format_saf_list]
    arch_target_buffer_interface_list=[obj.getSubcomponentById(target_id).getInterface() for target_id in arch_format_saf_target_list]
    arch_format_saf_ranks_list=[format_saf.getAttributes()[0] for format_saf in arch_format_saf_list]

    arch_topology=obj.getTopology()
    arch_topology_component_list=arch_topology.getComponentList()
    arch_topology_net_list=arch_topology.getNetList()

    for idx in range(len(arch_format_saf_list)):
        # Concretize format SAF to format uarch
        #print(arch_format_saf_ranks_list[idx])
        print(arch_target_buffer_interface_list[idx])
        print(obj.getSAFList()[0].getAttributes())
        buffer_id=arch_format_saf_target_list[idx]        
        format_uarch = genFormatUarchWithHole(buffer_id+"_datatype_format_uarch",arch_format_saf_ranks_list[idx])

        # Add format uarch to architecture
        arch_topology_component_list.append(format_uarch)

        # Net list setup
        format_uarch_id=format_uarch.getId()
        format_uarch_interface_list=format_uarch.getInterface()
        buffer_port_id_list=[port.getId() for port in arch_target_buffer_interface_list[idx]]

        for format_uarch_port in format_uarch_interface_list:
            format_uarch_port_id=format_uarch_port.getId()
            buffer_port_id=formatUarchPortIdToBufferPortIdMapping(format_uarch_port_id)
            print(buffer_port_id)
            print(buffer_port_id_list)
            assert(buffer_port_id in buffer_port_id_list) # Assert mapped buffer port exists
            format_uarch_port_id=format_uarch_id+'.'+format_uarch_port_id
            buffer_port_id=buffer_id+'.'+buffer_port_id
            print('\nformat_uarch_port_id:',format_uarch_port_id,'buffer_port_id:',buffer_port_id,'\n')

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

    print("\nobj:\n\n",obj,'\n\n')

    return obj



# --- predicate

def predicateIsArchitectureHasFormatSAF(obj):
    '''Object is an architecture with at least one format SAF'''
    print(obj.getId())
    return type(obj).__name__ == 'Architecture' and ('format' in [saf.getCategory() for saf in obj.getSAFList()])

# - Format uarch rewrite rules

# -- TransformTopologicalHoleToPerRankMdParserTopology: For a format uarch with a topological hole, fill the hole with a topology comprising one MetadataParser primitive per traversed tensor rank at this buffer level

def genPrimitiveMetadataParser(primitive_id, fmt):
    '''Helper function for format uarch testbench. Generate a MetadataParser primitive.'''

    # Category
    primitive_category='MetadataParser'

    # Attributes
    primitive_attributes=[FormatType.fromIdValue('format',fmt)]

    # Interface
    # - md_in
    net_type=NetType.fromIdValue('TestNetType','md')
    format_type=FormatType.fromIdValue('TestFormatType',fmt)    
    port_md_in=Port.fromIdDirectionNetTypeFormatType('md_in', 'in', net_type, format_type)    

    # - at_bound_out
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')
    at_bound_out=Port.fromIdDirectionNetTypeFormatType('at_bound_out', 'out', net_type, format_type)

    # - build interface
    primitive_interface=[port_md_in,at_bound_out]

    return Primitive.fromIdCategoryAttributesInterface(primitive_id, primitive_category, primitive_attributes, primitive_interface)

def generateFormatUarchTopology(rank_format_strs):
   # Topology ID
    topology_id='TestTopology'

    # Component list setup
    component_list=[]
    for idx in range(len(rank_format_strs)):
        fmt_str=rank_format_strs[idx]
        component_list.append(genPrimitiveMetadataParser('TestMetadataParser'+str(idx), fmt_str))
        

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
