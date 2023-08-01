'''SAFinfer tool infers microarchitecture topology from Sparseloop configuration files'''

import util.sparseloop_config_processor as sl_config
from util.taxonomy.serializableobject import *
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *
import argparse
import copy


yaml.Dumper.ignore_aliases = lambda *args : True

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

        # -- pos_in ports
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','addr')    
        port_pos_in=Port.fromIdDirectionNetTypeFormatType('pos_in'+str(idx), 'in', net_type, format_type)   

        # -- at_bound_in ports
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','?')    
        port_at_bound_in=Port.fromIdDirectionNetTypeFormatType('at_bound_in'+str(idx), 'in', net_type, format_type)   

        primitive_interface.append(port_md_out)
        primitive_interface.append(port_pos_in)
        primitive_interface.append(port_at_bound_in)



    return Primitive.fromIdCategoryAttributesInterface(buffer_stub_id, primitive_category, primitive_attributes, primitive_interface)


def loadProb(filename):
    '''Load Sparseloop problem file'''
    return sl_config.load_config_yaml(filename)

def loadMap(filename):
    '''Load Sparseloop map file'''
    return sl_config.load_config_yaml(filename)

'''
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

    return arch, saf_spec
'''

def topology_with_holes_from_bindings(arch, fmt_iface_bindings, skip_bindings, data_space_dict_list):

    # Fix mismatch in conventions
    fmt_str_convert={"UOP":"U", "RLE":"R", "C":"C","B":"B"}

    # Extract buffer hierarchy
    buffer_hierarchy=[buffer for buffer in list(sl_config.flatten_arch_wrapper(arch).keys()) if buffer != 'MAC']

    # Compute flattened port indices
    port_idx={buffer:{dtype:[0 for fmt_iface in fmt_iface_bindings[buffer][dtype]] for dtype in data_space_dict_list} for buffer in buffer_hierarchy}
    for buffer in buffer_hierarchy:
        idx=0
        for dtype in data_space_dict_list:
            for jdx in range(len(port_idx[buffer][dtype])):
                port_idx[buffer][dtype][jdx]=idx
                idx+=1
    #print(port_idx)

    # Generate buffer stubs
    buffer_stub_list=[]
    saf_list=[]
    for buffer in buffer_hierarchy:
        datatype_fmt_ifaces=fmt_iface_bindings[buffer]
        # - Flatten the interface formats associated with this buffer stub
        flat_rank_fmts=[]
        for dtype in datatype_fmt_ifaces:
            flat_rank_fmts.extend([fmt_str_convert[fmt_iface['format']] for fmt_iface in datatype_fmt_ifaces[dtype]])
        flat_rank_fmts=[FormatType.fromIdValue('format',fmt_str) for fmt_str in flat_rank_fmts]
        # - Create the buffer stub
        buffer_stub=genBufferStubByName(buffer, flat_rank_fmts)
        buffer_stub_list.append(buffer_stub)
        # - Create the Format SAF if sparse traversal support is required
        if len(flat_rank_fmts)>0:
            fmt_saf=SAF.fromIdCategoryAttributesTarget('format_saf', 'format', [flat_rank_fmts], buffer)
            saf_list.append(fmt_saf)

    # Generate action-optimization SAFs
    skip_bindings=copy.deepcopy(skip_bindings)
    for bdx in range(len(skip_bindings)):
        skip_binding=skip_bindings[bdx]
        # First, transform skip binding to use flattened port indices
        target_buffer=skip_binding['target']['buffer']
        target_dtype=skip_binding['target']['dtype']
        target_fmt_iface=skip_binding['target']['fmt_iface']
        condition_buffer=skip_binding['condition']['buffer']
        condition_dtype=skip_binding['condition']['dtype']
        condition_fmt_iface=skip_binding['condition']['fmt_iface']        

        target_fmt_iface_flat=port_idx[target_buffer][target_dtype][target_fmt_iface]
        condition_fmt_iface_flat=port_idx[condition_buffer][condition_dtype][condition_fmt_iface]

        skip_binding['target']['fmt_iface']=target_fmt_iface_flat
        skip_binding['condition']['fmt_iface']=condition_fmt_iface_flat
        skip_bindings[bdx]=skip_binding

        # Second, create skipping SAF
        skipping_saf=SAF.fromIdCategoryAttributesTarget('skipping_saf', 'skipping', [[target_buffer,target_fmt_iface_flat,condition_buffer,condition_fmt_iface_flat]], target_buffer)
        saf_list.append(skipping_saf)

    [print(saf) for saf in saf_list]
    taxo_arch=genArch(buffer_stub_list, buffer_hierarchy, saf_list)

    return taxo_arch   


        

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--saftaxolib',default='saftaxolib/')
    parser.add_argument('-i','--dir-in',default='')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml')
    parser.add_argument('-m','--map',default='ref_input/map.yaml')
    parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml')
    parser.add_argument('-o','--dir-out',default='')
    parser.add_argument('-b','--binding-out',default='ref_output/bindings.yaml')
    parser.add_argument('-t','--topology-out',default='ref_output/new_arch.yaml')
    parser.add_argument('-r','--reconfigurable-arch',default=False)    
    args = parser.parse_args()

    print("SAFinfer.\n")

    print("Parsing input files:")

    if len(args.dir_in)>0:
        print("- arch:",args.dir_in+'arch.yaml')
        arch=sl_config.load_config_yaml(args.dir_in+'arch.yaml')
        print("- map:",args.dir_in+'map.yaml')
        mapping=sl_config.load_config_yaml(args.dir_in+'map.yaml')
        print("- prob:",args.dir_in+'prob.yaml')
        prob=sl_config.load_config_yaml(args.dir_in+'prob.yaml')
        print("- sparseopts:",args.dir_in+'sparseopts.yaml')
        sparseopts=sl_config.load_config_yaml(args.dir_in+'sparseopts.yaml')        
    else:    
        print("- arch:",args.arch)
        arch=sl_config.load_config_yaml(args.arch)
        print("- map:",args.map)
        mapping=sl_config.load_config_yaml(args.map)
        print("- prob:",args.prob)
        prob=sl_config.load_config_yaml(args.prob)
        print("- sparseopts:",args.sparseopts)
        sparseopts=sl_config.load_config_yaml(args.sparseopts)

    if not args.reconfigurable_arch:
        print("- fixed arch (reconfigurable-arch == False)")
    else:
        print("- ERROR reconfigurable arch not yet supported")
        assert(False)

    #arch, saf_spec=loadSparseloopArchitecture(args.in_yaml)

    print("\nComputing bindings.")

    # data_space_dict_list, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities=sl_config.data_space_dict_list_from_sl_prob(prob)    
    # fmt_iface_bindings, pgens, buffer_loop_binding, loop_to_iface_map=sl_config.bind_format_iface(arch, mapping, prob, sparseopts)
    # skip_bindings=sl_config.bind_action_optimization(arch, mapping, prob, sparseopts, fmt_iface_bindings, loop_to_iface_map)

    # Parse the dense problem
    # - data_space_dict_list
    # - prob_coeff_list
    # - prob_instance_rank_sizes
    # - prob_instance_densities
    data_space_dict_list, prob_coeff_list, prob_instance_rank_sizes, prob_instance_densities=sl_config.data_space_dict_list_from_sl_prob(prob)    
    
    # Bind representation-format processing interfaces to architectural buffers
    # (mapping- and problem-dependent approach)
    # - fmt_iface_bindings
    # - pgens
    # - buffer_loop_binding
    # - loop_to_iface_map
    fmt_iface_bindings, pgens, buffer_loop_binding, loop_to_iface_map=sl_config.bind_format_iface(arch, mapping, prob, sparseopts)

    # Bind action-optimization SAFs to archtiectural buffers
    # - skip_bindings
    skip_bindings=sl_config.bind_action_optimization(arch, mapping, prob, sparseopts, fmt_iface_bindings, loop_to_iface_map)    


    bind_out_path=args.binding_out
    topo_out_path=args.topology_out

    if len(args.dir_out) > 0:
        bind_out_path=args.dir_out+'bindings.yaml'
        topo_out_path=args.dir_out+'new_arch.yaml'

    print("- Saving to",bind_out_path)
    with open(bind_out_path, 'w') as fp:
        yaml.dump(fmt_iface_bindings,fp, default_flow_style=False)

    # Create a data structure to represent architectural buffers and SAF microarchitectures
    # Problem- and mapping-independent, given fmt_iface_bindings, skip_bindings
    # and data_space_dict_list have already been computed
    print("\nRealizing microarchitecture with topological holes, based on bindings.\n")
    taxo_arch=topology_with_holes_from_bindings(arch, fmt_iface_bindings, skip_bindings, data_space_dict_list)

    print("Performing arch inference...")

    rules_engine = RulesEngine([args.saftaxolib+'base_ruleset', \
                                args.saftaxolib+'primitive_md_parser_ruleset', \
                                args.saftaxolib+'format_uarch_ruleset'])
                                #args.saftaxolib+'skipping_uarch_ruleset'])

    rules_engine.preloadRules()
    result=rules_engine.run(taxo_arch)

    outcome=result[0]
    if outcome:
        print("SUCCESS")
        print("Saving to",topo_out_path,"...")
        inferred_arch=result[-1][-1]
        inferred_arch.dump(topo_out_path)
    else:
        print("FAILURE")