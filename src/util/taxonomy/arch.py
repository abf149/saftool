import util.sparseloop_config_processor as sl_config
from util.taxonomy.serializableobject import *
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.taxonomy.rulesengine import *
import copy

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