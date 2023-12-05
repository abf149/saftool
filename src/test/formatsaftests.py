'''Format SAF regression testbench'''


from core.taxonomy.serializableobject import SerializableObject
from core.taxonomy.expressions import *
from core.taxonomy.designelement import *
from solver.solve import *

def genArch(buffer_stub, arch_saf_list):

    # Architecture id
    arch_id="TestArchitecture"

    # Topology

    # - Topology ID
    topology_id='TestTopology'

    # - Component list setup
    component_list=[buffer_stub]

    # - Net list setup
    # -- build Net list
    net_list=[]

    # - build topology
    architecture_topology=Topology.fromIdNetlistComponentList(topology_id,net_list,component_list)

    # Buffer hierarchy
    buffer_hierarchy=[buffer_stub.getId()]

    arch=Architecture.fromIdSAFListTopologyBufferHierarchy(arch_id,arch_saf_list,architecture_topology,buffer_hierarchy)

    return arch

def genBufferStubByName(buffer_stub_id, rank_format_list_str):
    '''Helper function for generating an architectural buffer stub. Generate a BufferStub primitive.'''

    # Category
    primitive_category='BufferStub'

    # Attributes
    primitive_attributes=[]

    # Interface
    # - build interface
    primitive_interface=[]    

    for idx in range(len(rank_format_list_str)):

        # -- md_out ports
        net_type=NetType.fromIdValue('TestNetType','md')
        format_type=FormatType.fromIdValue('TestFormatType','?')    
        port_md_out=Port.fromIdDirectionNetTypeFormatType('md_out'+str(idx), 'out', net_type, format_type)   

        # -- at_bound_in ports
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','?')    
        port_at_bound_in=Port.fromIdDirectionNetTypeFormatType('at_bound_in'+str(idx), 'in', net_type, format_type)   

        primitive_interface.append(port_md_out)
        primitive_interface.append(port_at_bound_in)



    return Primitive.fromIdCategoryAttributesInterface(buffer_stub_id, primitive_category, primitive_attributes, primitive_interface)


def genFormatSAFTargetingBuffer(rank_format_list_str, target_buffer_name):
    '''Helper function for format SAF testbench. Generate an example format SAF with a give rank format list (with ranks in string format) and the name of the target buffer for the SAF'''

    # Id
    saf_id='TestFormatSAF'

    # Category
    saf_category='format'

    # Attributes
    rank_format_list=[FormatType.fromIdValue('format',fmt_str) for fmt_str in rank_format_list_str]
    saf_attributes=[rank_format_list]

    # build SAF
    saf=SAF.fromIdCategoryAttributesTarget(saf_id,saf_category,saf_attributes,target_buffer_name)

    return saf

def do_tests():
    '''Tests of ruleset for concretizing format SAF to format uarch'''

    print("\n\n")

    print("Tests of ruleset for concretizing format SAF to format uarch")

    print("\n\n")    

    # Setup

    print("- Setup")
    print("-- Create a buffer stub TestBuffer; print; dump")
    buffer_stub=genBufferStubByName('TestBuffer', ['C','B'])
    print(buffer_stub)
    buffer_stub.dump('buffer_stub_test.yaml')
    print("-- Create a format SAF; print; dump")
    format_saf=genFormatSAFTargetingBuffer(['C','B'], 'TestBuffer')
    print(format_saf)
    format_saf.dump('format_saf_test.yaml')
    print("-- Create an architecture with a single buffer level and a format SAF with a attribute specifying format at each rank; print; dump")
    arch=genArch(buffer_stub,[format_saf])
    print(arch)
    arch.dump('arch_test.yaml')
    print(arch)
    print("- Run Rules Engine against architecture; print; dump")
    print("\n\n")   

    base_rule_set_path='saftaxolib/base_ruleset'
    primitive_md_parser_rule_set_path='saftaxolib/primitive_md_parser_ruleset'
    format_uarch_rule_set_path='saftaxolib/format_uarch_ruleset'

    print("-- Load topology validation rules (",base_rule_set_path,",",primitive_md_parser_rule_set_path,',',format_uarch_rule_set_path,") into RulesEngine & preload rules")
    rules_engine = RulesEngine([base_rule_set_path,primitive_md_parser_rule_set_path,format_uarch_rule_set_path])
    rules_engine.preloadRules()
    print("-- run()")

    print("\n\n")   

    result=rules_engine.run(arch)    
    print(result[-1][-1])
    result[-1][-1].dump('inferred_architecture_with_format_saf_test.yaml')
    #print("-- Dump inferred microarchitecture")
    #result[1][-1].dump('incomplete_component_interface_attribute_type_test_SOLVED.yaml')    