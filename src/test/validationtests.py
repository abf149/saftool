from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *

def genDummyComponent(break_net_type=False, break_format_type=False):
    '''Helper function for the validation testbench. Generate a dummy component. Optionally introduce invalidate NetType or FormatType.'''

    # Topology ID
    topology_id='TestTopology'

    # Net list setup
    # - Net connecting data ports
    net_type=NetType.fromIdValue('TestNetType','data')
    format_type=FormatType.fromIdValue('TestFormatType','null')
    port_id_list=['data_in','data_out']
    net_data=Net.fromIdAttributes('TestDataNet', net_type, format_type, port_id_list)

    # - Net connecting metadata (md) ports
    net_type=NetType.fromIdValue('TestNetType','md')
    format_type=FormatType.fromIdValue('TestFormatType','C')
    port_id_list=['md_in','md_out']
    net_md=Net.fromIdAttributes('TestMDNet', net_type, format_type, port_id_list)

    # - Net connecting position (pos) ports
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')
    port_id_list=['pos_in','pos_out']
    net_pos=Net.fromIdAttributes('TestPosNet', net_type, format_type, port_id_list)

    # - build Net list
    net_list=[net_data,net_md,net_pos]

    # Component list setup
    component_list=[]
    
    # build topology
    component_topology=Topology.fromIdNetlistComponentList(topology_id,net_list,component_list)

    # Id
    component_id='TestComponent'

    # Category
    component_category='TestComponentCategory'

    # Attributes
    attribute0='attribute0'
    attribute1=1
    attribute2=FormatType.fromIdValue('TestAttributeFormatType','C')
    component_attributes=[attribute0,attribute1,attribute2]

    # Interface
    # - data_in, data_out ports
    net_type=NetType.fromIdValue('TestNetType','data')
    format_type=FormatType.fromIdValue('TestFormatType','null')
    port_data_in=Port.fromIdDirectionNetTypeFormatType('data_in', 'in', net_type, format_type)
    port_data_out=Port.fromIdDirectionNetTypeFormatType('data_out', 'out', net_type, format_type)

    # - md_in, md_out ports
    md_port_in_net_type_value='md'
    md_port_in_format_type_value='C'
    net_type=NetType.fromIdValue('TestNetType',md_port_in_net_type_value)
    format_type=FormatType.fromIdValue('TestFormatType',md_port_in_format_type_value)    
    port_md_in=Port.fromIdDirectionNetTypeFormatType('md_in', 'in', net_type, format_type)    
    if break_net_type:
        # Invalidate the net's NetType
        md_port_in_net_type_value='data'
    if break_format_type:
        # Invalidate the net's Format
        md_port_in_format_type_value='U'
    net_type=NetType.fromIdValue('TestNetType',md_port_in_net_type_value)
    format_type=FormatType.fromIdValue('TestFormatType',md_port_in_format_type_value)    
    port_md_out=Port.fromIdDirectionNetTypeFormatType('md_out', 'out', net_type, format_type)

    # - pos_in, pos_out ports
    net_type=NetType.fromIdValue('TestNetType','pos')
    format_type=FormatType.fromIdValue('TestFormatType','addr')
    port_pos_in=Port.fromIdDirectionNetTypeFormatType('pos_in', 'in', net_type, format_type)
    port_pos_out=Port.fromIdDirectionNetTypeFormatType('pos_out', 'out', net_type, format_type)

    # - build interface
    component_interface=[port_data_in,port_data_out,port_md_in,port_md_out,port_pos_in,port_pos_out]

    # build component
    component=Component.fromIdCategoryAttributesInterfaceTopology(component_id,component_category,component_attributes,component_interface,component_topology)

    return component

def do_tests():
    '''Tests of generic component validation rules'''

    print("\n\n")

    print("Tests of generic component validation rules")

    print("\n\n")    

    # Setup

    print("- Setup")
    print("-- Create dummy flat component with no subcomponents & nets directly connecting the interface ports; print")
    dummy_component=genDummyComponent()
    dummy_component_break_net_type=genDummyComponent(break_net_type=True)
    dummy_component_break_format_type=genDummyComponent(break_format_type=True)    
    print(dummy_component)

    # Topology validation rules

    print("\n\n")   

    print("- Topology validation rules, flat dummy architecture")
    rule_set_path='saftaxolib/base_ruleset'

    print("\n\n")   

    print("-- For known good dummy topology, load topology validation rules (",rule_set_path,") into RulesEngine & preload rules")
    rules_engine = RulesEngine([rule_set_path])
    rules_engine.preloadRules()
    print("-- run()")

    print("\n\n")   

    rules_engine.run(dummy_component)
    print("-- For known bad dummy topology (port net-type mismatch on same net), load topology validation rules (",rule_set_path,") into RulesEngine & preload rules")
    try:
        rules_engine.run(dummy_component_break_net_type)    
    except:
        print("EXCEPTION: this is expected for a known bad dummy topology")

    print("\n\n")   

    print("-- For known bad dummy topology (port format-type mismatch on same net), load topology validation rules (",rule_set_path,") into RulesEngine & preload rules")
    try:
        rules_engine.run(dummy_component_break_format_type)    
    except:
        print("EXCEPTION: this is expected for a known bad topology")