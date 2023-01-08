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

    # Leader/left interface
    md_format_type=FormatType.fromIdValue('TestFormatType','?') 
    pos_format_type=FormatType.fromIdValue('TestFormatType','addr')

    # -- md_in port
    net_type=NetType.fromIdValue('TestNetType','md')
    port_md_in0=Port.fromIdDirectionNetTypeFormatType('md_in0', 'in', net_type, md_format_type)

    # -- pos_out port
    net_type=NetType.fromIdValue('TestNetType','pos')
    port_pos_out0=Port.fromIdDirectionNetTypeFormatType('pos_out0', 'out', net_type, pos_format_type)   

    # Follower/right interface

    # -- md_in port
    net_type=NetType.fromIdValue('TestNetType','md')
    port_md_in1=Port.fromIdDirectionNetTypeFormatType('md_in1', 'in', net_type, md_format_type)

    # -- pos_out port
    net_type=NetType.fromIdValue('TestNetType','pos')
    port_pos_out1=Port.fromIdDirectionNetTypeFormatType('pos_out1', 'out', net_type, pos_format_type)       

    # Interface
    component_interface=[port_md_in0, port_pos_out0, port_md_in1, port_pos_out1] 

    # Create topological hole
    component_topology=[]
    topology_id='TestTopologyHole'
    component_topology=Topology.holeFromId(topology_id)

    # build component
    component=Component.fromIdCategoryAttributesInterfaceTopology(skipping_uarch_id,component_category,component_attributes,component_interface,component_topology)

    return component

def concretizeArchitectureSkippingSAFsToSkippingUarches(obj):
    '''Object is an architecture with at least one skipping SAF; concretize skipping SAF(s) to skipping uarch(es) and critically, DELETE THE SKIPPING SAFS'''
    
    arch_saf_list=obj.getSAFList()

    arch_skipping_saf_list=[skipping_saf for skipping_saf in arch_saf_list if skipping_saf.getCategory() == 'skipping']
    arch_non_skipping_saf_list=[skipping_saf for skipping_saf in arch_saf_list if skipping_saf.getCategory() != 'skipping']

    arch_topology=obj.getTopology()
    arch_topology_component_list=arch_topology.getComponentList()
    arch_topology_net_list=arch_topology.getNetList()

    for skipping_saf in arch_skipping_saf_list:
        attrib=skipping_saf.attributes[0]

        # Unpack SAF attributes & derive skipping uarch attributes
        target_buffer=attrib[0]
        target_port_suffix=attrib[1]
        condition_buffer=attrib[2]
        condition_port_suffix=attrib[3]        
        skipping_uarch_id='SkippingUarch'+target_buffer+str(target_port_suffix)+condition_buffer+str(condition_port_suffix)
        skipping_uarch_follower_right_md_in_port=skipping_uarch_id+'.md_in1'
        skipping_uarch_follower_right_pos_out_port=skipping_uarch_id+'.pos_out1'     
        skipping_uarch_leader_left_md_in_port=skipping_uarch_id+'.md_in0'
        skipping_uarch_leader_left_pos_out_port=skipping_uarch_id+'.pos_out0'       

        # Generate skipping uarch        
        skipping_uarch=genSkippingUarchWithHole(skipping_uarch_id)

        # Add skipping uarch to architecture
        arch_topology_component_list.append(skipping_uarch) 

        # Left/leader metadata net       
        net_type=NetType.fromIdValue('TestNetType','md')
        format_type=FormatType.fromIdValue('TestFormatType','?')
        condition_buffer_md_out_port=condition_buffer+'.md_out'+str(condition_port_suffix)
        port_id_list=[skipping_uarch_leader_left_md_in_port,condition_buffer_md_out_port]
        net_leader_left_md=Net.fromIdAttributes('net_'+skipping_uarch_leader_left_md_in_port+'_'+condition_buffer_md_out_port, net_type, format_type, port_id_list)

        # Left/leader position net       
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','addr')
        condition_buffer_pos_in_port=condition_buffer+'.pos_in'+str(condition_port_suffix)
        port_id_list=[skipping_uarch_leader_left_pos_out_port,condition_buffer_pos_in_port]
        net_leader_left_pos=Net.fromIdAttributes('net_'+skipping_uarch_leader_left_pos_out_port+'_'+condition_buffer_pos_in_port, net_type, format_type, port_id_list)

        # Right/follower metadata net       
        net_type=NetType.fromIdValue('TestNetType','md')
        format_type=FormatType.fromIdValue('TestFormatType','?')
        target_buffer_md_out_port=target_buffer+'.md_out'+str(target_port_suffix)
        port_id_list=[skipping_uarch_follower_right_md_in_port,target_buffer_md_out_port]
        net_follower_right_md=Net.fromIdAttributes('net_'+skipping_uarch_follower_right_md_in_port+'_'+target_buffer_md_out_port, net_type, format_type, port_id_list)

        # Right/follower position net       
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','addr')
        target_buffer_pos_in_port=target_buffer+'.pos_in'+str(target_port_suffix)
        port_id_list=[skipping_uarch_follower_right_pos_out_port,target_buffer_pos_in_port]
        net_follower_right_pos=Net.fromIdAttributes('net_'+skipping_uarch_follower_right_pos_out_port+'_'+target_buffer_pos_in_port, net_type, format_type, port_id_list)

        arch_topology_net_list.extend([net_leader_left_md,net_leader_left_pos,net_follower_right_md,net_follower_right_pos])

    arch_topology.setComponentList(arch_topology_component_list)
    arch_topology.setNetList(arch_topology_net_list)
    obj.setTopology(arch_topology)
    # Delete skipping SAFs
    obj.setSAFList(arch_non_skipping_saf_list)

    print("\nobj:\n\n",obj,'\n\n')

    return obj



# --- predicate

def predicateIsArchitectureHasSkippingSAF(obj):
    '''Object is an architecture with at least one skipping SAF'''
    print(obj.getId())
    return type(obj).__name__ == 'Architecture' and ('skipping' in [saf.getCategory() for saf in obj.getSAFList()])

# -- TransformTopologicalHoleToSkippingUarchTopology
# --- rewrite rule

def genPrimitivePgen(pgen_name):
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

def genPrimitiveIntersect(intersect_name):
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

def generateSkippingUarchTopology():
   # Topology ID
    topology_id='TestTopology'

    # Component list setup
    intersect = genPrimitiveIntersect()
    pgen_leader_left = genPrimitivePgen("leader_left")
    pgen_follower_right = genPrimitivePgen("follower_right")    
    component_list=[genPrimitiveIntersect("intersect"), genPrimitivePgen("pgen_leader_left"), genPrimitivePgen("pgen_follower_right")]

    # Net list setup
    net_type=NetType.fromIdValue('TestNetType','md')
    format_type=FormatType.fromIdValue('TestFormatType','?')    
    # - Nets connecting metadata (md) ports to primitives, position (pos) ports to primitives
    # - Skipping uarch ports: md_in0 pos_out0 (leader/left) md_in1 pos_out1 (follower/right) md format is controlled by intersect format attribute
    # - Intersect ports: md_in0 (leader/left) md_in1 (follower/right) md_out; md format is controlled by intersect format attribute
    # - Pgen ports: md_in post_out; md format is controlled by pgen format attribute
    # - Components: [intersect, pgen_left/leader, pgen_right/follower]
    # - Netlist:
    #   - [md_in0,intersect.md_in0]
    port_id_list=['md_in0','intersect.md_in0']
    net_md_in0_intersect_md_in0=Net.fromIdAttributes('net_md_in0_intersect_md_in0', net_type, format_type, port_id_list)
    #   - [md_in1,intersect.md_in1]
    port_id_list=['md_in1','intersect.md_in1']
    net_md_in1_intersect_md_in1=Net.fromIdAttributes('net_md_in1_intersect_md_in1', net_type, format_type, port_id_list)
    #   - [intersect.md_out, pgen_left/leader.md_in, pgen_right/follower.md_in]
    port_id_list=['intersect.md_out','pgen_leader_left.md_in','pgen_follower_right.md_in']
    net_intersect_out=Net.fromIdAttributes('net_intersect_out', net_type, format_type, port_id_list)
    #   - [pgen_left/leader.pos_out,pos_out0]
    port_id_list=['pgen_leader_left.pos_out','pos_out0']
    net_pos_left=Net.fromIdAttributes('net_intersect_out', net_type, format_type, port_id_list)
    #   - [pgen_right/follower.pos_out,pos_out1]


    
    port_id_list=['d_in'+str(idx),'TestMetadataParser'+str(idx)+'.md_in']

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

def transformTopologicalHoleToSkippingUarchTopology(obj):
    '''Fill the topological hole with a leader-follower skipping uarch topology. TODO: support bidirectional'''

    obj.setTopology(generateSkippingUarchTopology())

    return obj

def predicateIsComponent(obj):
    return type(obj).__name__ == 'Component'

def predicateIsSkippingUarch(obj):
    return obj.getCategory() == 'SkippingUarch'

def predicateHasTopologicalHole(obj):
    return obj.getTopology().isHole()

def predicateIsComponentIsSkippingUarchHasTopologicalHole(obj):
    return predicateIsComponent(obj) and predicateIsSkippingUarch(obj) and predicateHasTopologicalHole(obj)


    

""" # - Format uarch rewrite rules

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
    return predicateIsComponent(obj) and predicateIsFormatUarch(obj) and predicateHasTopologicalHole(obj) """
