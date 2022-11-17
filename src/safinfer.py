'''SAFinfer tool infers microarchitecture topology from Sparseloop configuration files'''

import util.sparseloop_config_processor as sl_config
from util.taxonomy.serializableobject import *
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *
import argparse


def genArch(buffer_stub_list, buffer_hierarchy, arch_saf_list):

    # Architecture id
    arch_id="TestArchitecture"

    # Topology

    # - Topology ID
    topology_id='TestTopology'

    # - Component list setup
    component_list=buffer_stub_list

    # - Net list setup
    # -- build Net list
    net_list=[]

    # - build topology
    architecture_topology=Topology.fromIdNetlistComponentList(topology_id,net_list,component_list)

    # Buffer hierarchy
    #buffer_hierarchy=[buffer_stub.getId()]

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

def loadArchitectureRecurse(hierarchical_arch):
    '''Recursive unwrapping of Sparseloop architecture'''
    res=[]
    for parent in hierarchical_arch:
        if 'local' in parent:
            # Append buffer-level names at this hierarchical level
            res.extend([lvl['name'] for lvl in parent['local']])
        if 'subtree' in parent:
            # Recurse to list of buffer subtrees below this node
            res.extend(loadArchitectureRecurse(parent['subtree']))

    return res

def loadArchitecture(filename):
    '''Wrapper for recursive flattening of Sparseloop architecture file'''
    return loadArchitectureRecurse(sl_config.load_config_yaml(filename)['architecture']['subtree'])

def loadProb(filename):
    '''Load Sparseloop problem file'''
    return sl_config.load_config_yaml(filename)

def loadMap(filename):
    '''Load Sparseloop map file'''
    return sl_config.load_config_yaml(filename)

def loadSparseloopArchitecture(filename):
    saf_spec=sl_config.SAFSpec(filename)

    blacklist=['MAC','BackingStorage']

    fmt_str_convert={"UOP":"U", "RLE":"R", "C":"C"}


    buffer_hierarchy=[lvl for lvl in saf_spec.getArchLevels()]
    buffer_safs=[saf_spec.getArchLevelSAFs(lvl) for lvl in buffer_hierarchy]
    
    # Extract format SAFs
    buffer_format_saf_ranks_list=[]
    processed_buffer_safs=[]
    buffer_stub_list=[]

    for idx in range(len(buffer_hierarchy)):
        if (not (buffer_hierarchy[idx] in blacklist)) and ('FormatSAF' in buffer_safs[idx]) and (buffer_safs[idx]['FormatSAF'] is not None):
            buffer_format_saf_ranks=[]
            datatype_format_safs=buffer_safs[idx]['FormatSAF'].sparseopts_representation_format_structure
            for jdx in range(len(datatype_format_safs)):
                sl_datatype=datatype_format_safs[jdx]['name']
                sl_rank_objs=datatype_format_safs[jdx]['ranks']
                sl_rank_str_list=[fmt_str_convert[sl_rank['format']] for sl_rank in sl_rank_objs]
                sl_rank_fmt_list=[FormatType.fromIdValue('format',fmt_str) for fmt_str in sl_rank_str_list]
                buffer_format_saf_ranks=sl_rank_fmt_list

            buffer_format_saf_ranks_list.append(buffer_format_saf_ranks)
            buffer_format_saf=SAF.fromIdCategoryAttributesTarget('format_saf', 'format', [buffer_format_saf_ranks], buffer_hierarchy[idx])
            processed_buffer_safs.append(buffer_format_saf)
            buffer_stub=genBufferStubByName(buffer_hierarchy[idx], buffer_format_saf_ranks)
            print(buffer_hierarchy[idx])
            print('-',[port.getId() for port in buffer_stub.getInterface()])
            print('-',[fmt_type.getValue() for fmt_type in buffer_format_saf.getAttributes()[0]])
            buffer_stub_list.append(buffer_stub)
        else:
            buffer_stub=genBufferStubByName(buffer_hierarchy[idx], [])
            buffer_stub_list.append(buffer_stub)
    
    arch=genArch(buffer_stub_list, buffer_hierarchy, processed_buffer_safs)    

    print('\n',buffer_format_saf_ranks_list,'\n')
    print('\n',[str(x) for x in buffer_format_saf_ranks_list[1]],'\n')
    print('\n',[str(saf) for saf in processed_buffer_safs],'\n')
    print('\n',[str(buffer) for buffer in buffer_stub_list],'\n')

    #arch.dump('sparseloop_processed_arch_test.yaml')

    return arch

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("in_yaml")
    parser.add_argument("out_yaml")
    args = parser.parse_args()

    print("Loading",args.in_yaml,"...")
    arch=loadSparseloopArchitecture(args.in_yaml)

    print("Performing arch inference...")
    rules_engine = RulesEngine(['saftaxolib/base_ruleset','saftaxolib/primitive_md_parser_ruleset','saftaxolib/format_uarch_ruleset'])
    rules_engine.preloadRules()
    result=rules_engine.run(arch)

    outcome=result[0]
    if outcome:
        print("SUCCESS")
        print("Savings to",args.out_yaml,"...")
        inferred_arch=result[-1][-1]
        inferred_arch.dump(args.out_yaml)
    else:
        print("FAILURE")
