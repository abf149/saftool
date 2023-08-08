'''Incomplete SAF uarch regression testbench'''

from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from solver.solve import *

def genPrimitiveMetadataParserWithUnknownAttributeAndInterfaceType(primitive_id):
    '''Helper function for format uarch testbench. Generate a MetadataParser primitive.'''

    # Category
    primitive_category='MetadataParser'

    # Attributes
    primitive_attributes=[FormatType.fromIdValue('format','?')]

    # Interface
    # - md_in
    net_type=NetType.fromIdValue('TestNetType','md')
    format_type=FormatType.fromIdValue('TestFormatType','?')    
    port_md_in=Port.fromIdDirectionNetTypeFormatType('md_in', 'in', net_type, format_type)    

    # - at_bound_out
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')
    at_bound_out=Port.fromIdDirectionNetTypeFormatType('at_bound_out', 'out', net_type, format_type)

    # - build interface
    primitive_interface=[port_md_in,at_bound_out]

    return Primitive.fromIdCategoryAttributesInterface(primitive_id, primitive_category, primitive_attributes, primitive_interface)

def genFormatUarchWithHoleOrUnknownTypes(useTopologicalHole):
    '''Helper function for incomplete format uarch testbench. Generate an example format uarch with either a topological hole, or a mix of unknown port and attribute types'''

    # Id
    component_id='TestFormatUarch'

    # Category
    component_category='FormatUarch'

    # Attributes
    rank_format_list=[FormatType.fromIdValue('format','C'),FormatType.fromIdValue('format','B')]
    component_attributes=[rank_format_list]

    # Interface

    # - md_in ports
    net_type=NetType.fromIdValue('TestNetType','md')
    format_type=FormatType.fromIdValue('TestFormatType','C')    
    port_md_in0=Port.fromIdDirectionNetTypeFormatType('md_in0', 'in', net_type, format_type)   
    format_type=FormatType.fromIdValue('TestFormatType','B')    
    port_md_in1=Port.fromIdDirectionNetTypeFormatType('md_in1', 'in', net_type, format_type)   

    # - at_bound_out ports
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')    
    port_at_bound_out0=Port.fromIdDirectionNetTypeFormatType('at_bound_out0', 'out', net_type, format_type)   
    port_at_bound_out1=Port.fromIdDirectionNetTypeFormatType('at_bound_out1', 'out', net_type, format_type)   

    # - build interface
    component_interface=[port_md_in0,port_at_bound_out0,port_md_in1,port_at_bound_out1]

    # Create topology
    component_topology=[]

    if useTopologicalHole:
        # - Create topological hole
        topology_id='TestTopologyHole'
        component_topology=Topology.holeFromId(id)
    else:
    # Topology ID
        topology_id='TestTopology'

        # Component list setup
        component_list=[genPrimitiveMetadataParserWithUnknownAttributeAndInterfaceType('TestMetadataParser0'),genPrimitiveMetadataParserWithUnknownAttributeAndInterfaceType('TestMetadataParser1')]

        # Net list setup

        # - Net connecting metadata (md) ports
        net_type=NetType.fromIdValue('TestNetType','md')
        format_type=FormatType.fromIdValue('TestFormatType','C')
        port_id_list=['md_in0','TestMetadataParser0.md_in']
        net_md0=Net.fromIdAttributes('TestMDNet0', net_type, format_type, port_id_list)
        format_type=FormatType.fromIdValue('TestFormatType','B')
        port_id_list=['md_in1','TestMetadataParser1.md_in']    
        net_md1=Net.fromIdAttributes('TestMDNet0', net_type, format_type, port_id_list)

        # - Net connecting position (pos) ports
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','addr')
        port_id_list=['at_bound_out0','TestMetadataParser0.at_bound_out']
        net_at_bound0=Net.fromIdAttributes('TestPosNet0', net_type, format_type, port_id_list)
        port_id_list=['at_bound_out1','TestMetadataParser1.at_bound_out']    
        net_at_bound1=Net.fromIdAttributes('TestPosNet1', net_type, format_type, port_id_list)

        # - build Net list
        net_list=[net_md0,net_md1,net_at_bound0,net_at_bound1]

        # build topology
        component_topology=Topology.fromIdNetlistComponentList(topology_id,net_list,component_list)

    # build component
    component=Component.fromIdCategoryAttributesInterfaceTopology(component_id,component_category,component_attributes,component_interface,component_topology)

    return component

def do_tests():
    '''Tests of rule set evaluation against incomplete microarchitectures which include topological holes and unknown attribute types'''

    print("\n\n")

    print("Tests of rule set evaluation against incomplete microarchitectures which include topological holes and unknown attribute types")

    print("\n\n")    

    # Setup

    print("- Setup")

    print("\n\n")

    print("-- Create format uarch component with a topological hole; print; dump")
    format_uarch_component=genFormatUarchWithHoleOrUnknownTypes(useTopologicalHole=True)
    import pprint
    pprint.pprint(str(format_uarch_component))
    format_uarch_component.dump('incomplete_component_hole_test.yaml')

    # Topology validation rules

    print("\n\n")   

    print("- Topology validation rules against incomplete format uarch (topological hole)")
    base_rule_set_path='saftaxolib/base_ruleset'
    primitive_md_parser_rule_set_path='saftaxolib/primitive_md_parser_ruleset'
    format_uarch_rule_set_path='saftaxolib/format_uarch_ruleset'    

    print("\n\n")   

    print("-- Load topology validation rules (",base_rule_set_path,",",primitive_md_parser_rule_set_path,',',format_uarch_rule_set_path,") into RulesEngine & preload rules")
    rules_engine = RulesEngine([base_rule_set_path,primitive_md_parser_rule_set_path,format_uarch_rule_set_path])
    rules_engine.preloadRules()
    print("-- run()")

    print("\n\n")   

    result=rules_engine.run(format_uarch_component)
    print(result)    
    print("-- Dump inferred microarchitecture")
    result[1][-1].dump('incomplete_component_hole_test_SOLVED.yaml')    

    print("\n\n")

    print("-- Create format uarch component with a primitives that have unknown interface and attribute types, and [C,B] tensor ranks; print; dump")
    format_uarch_component=genFormatUarchWithHoleOrUnknownTypes(useTopologicalHole=False)
    import pprint
    pprint.pprint(str(format_uarch_component))
    format_uarch_component.dump('incomplete_component_interface_attribute_type_test.yaml')

    # Topology validation rules

    print("\n\n")   

    print("- Topology validation rules against incomplete format uarch (unknown interface/attributes)")
    base_rule_set_path='saftaxolib/base_ruleset'
    primitive_md_parser_rule_set_path='saftaxolib/primitive_md_parser_ruleset'
    format_uarch_rule_set_path='saftaxolib/format_uarch_ruleset'

    print("\n\n")   

    print("-- Load topology validation rules (",base_rule_set_path,",",primitive_md_parser_rule_set_path,',',format_uarch_rule_set_path,") into RulesEngine & preload rules")
    rules_engine = RulesEngine([base_rule_set_path,primitive_md_parser_rule_set_path,format_uarch_rule_set_path])
    rules_engine.preloadRules()
    print("-- run()")

    print("\n\n")   

    result=rules_engine.run(format_uarch_component)    
    print(result)
    print("-- Dump inferred microarchitecture")
    result[1][-1].dump('incomplete_component_interface_attribute_type_test_SOLVED.yaml')    

