'''Incomplete SAF uarch regression testbench'''

from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *

def genFormatUarch():
    '''Helper function for format uarch testbench. Generate an example format uarch.'''

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

   # Create topological hole
    topology_id='TestTopologyHole'
    component_topological_hole=Topology.holeFromId(id)

    # build component
    component=Component.fromIdCategoryAttributesInterfaceTopology(component_id,component_category,component_attributes,component_interface,component_topological_hole)

    return component

def do_tests():
    '''Tests of rule set evaluation against incomplete microarchitectures which include topological holes and unknown attribute types'''

    print("\n\n")

    print("Tests of rule set evaluation against incomplete microarchitectures which include topological holes and unknown attribute types")

    print("\n\n")    

    # Setup

    print("- Setup")
    print("-- Create format uarch component with a topological hole and [C,B] tensor ranks; print; dump")
    format_uarch_component=genFormatUarch()
    import pprint
    pprint.pprint(str(format_uarch_component))
    format_uarch_component.dump('incomplete_component_test.yaml')

    # Topology validation rules

    print("\n\n")   

    print("- Topology validation rules against incomplete format uarch")
    base_rule_set_path='saftaxolib/base_ruleset'
    primitive_md_parser_rule_set_path='saftaxolib/primitive_md_parser_ruleset'

    print("\n\n")   

    print("-- Load topology validation rules (",base_rule_set_path,",",primitive_md_parser_rule_set_path,") into RulesEngine & preload rules")
    rules_engine = RulesEngine([base_rule_set_path,primitive_md_parser_rule_set_path])
    rules_engine.preloadRules()
    print("-- run()")

    print("\n\n")   

    rules_engine.run(format_uarch_component)