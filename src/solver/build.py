'''Library for constructing a SAF microrarchitecture inference problem'''
from util.notation.microarchitecture import SAFFormat, SAFSkipping, BufferStub, fmt_str_convert
from util.taxonomy.designelement import Topology,Architecture,NetType,FormatType,Port,Primitive, SAF
import util.sparseloop_config_processor as sl_config, copy

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

def topology_with_holes_from_bindings(arch, fmt_iface_bindings, skip_bindings, dtype_list):

    # Fix mismatch in conventions
    #fmt_str_convert={"UOP":"U", "RLE":"R", "C":"C","B":"B"}

    # Extract buffer hierarchy
    buffer_hierarchy=[buffer for buffer in list(sl_config.flatten_arch_wrapper(arch).keys()) if buffer != 'MAC']

    # Compute flattened port indices
    port_idx={buffer:{dtype:[0 for fmt_iface in fmt_iface_bindings[buffer][dtype]] for dtype in dtype_list} for buffer in buffer_hierarchy}
    for buffer in buffer_hierarchy:
        idx=0
        for dtype in dtype_list:
            for jdx in range(len(port_idx[buffer][dtype])):
                port_idx[buffer][dtype][jdx]=idx
                idx+=1

    # Generate buffer stubs
    buffer_stub_list=[]
    saf_list=[]
    for buffer in buffer_hierarchy:
        datatype_fmt_ifaces=fmt_iface_bindings[buffer]

        if sum([len(datatype_fmt_ifaces[dtype]) for dtype in datatype_fmt_ifaces])>0:
            fmt_saf=SAFFormat.copy() \
                             .target(buffer) \
                             .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree") \
                             .build('format_saf')

            buffer_stub=BufferStub.copy() \
                                  .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree") \
                                  .generate_ports("fibertree","fibertree") \
                                  .build(buffer)

            buffer_stub_list.append(buffer_stub)
            saf_list.append(fmt_saf)

    # Generate action-optimization SAFs
    skip_bindings=copy.deepcopy(skip_bindings)
    for bdx in range(len(skip_bindings)):
        skip_binding=skip_bindings[bdx]
        # First, transform skip binding to use flattened port indices
        # TODO: format interfaces don't need to be determined here
        target_buffer=skip_binding['target']['buffer']
        target_dtype=skip_binding['target']['dtype']
        target_fmt_iface=-1 #skip_binding['target']['fmt_iface']
        condition_buffer=skip_binding['condition']['buffer']
        condition_dtype=skip_binding['condition']['dtype']
        condition_fmt_iface=-1 #skip_binding['condition']['fmt_iface']        

        target_fmt_iface_flat=port_idx[target_buffer][target_dtype][0] #target_fmt_iface
        condition_fmt_iface_flat=port_idx[condition_buffer][condition_dtype][0] #condition_fmt_iface

        skip_binding['target']['fmt_iface']=-1 #target_fmt_iface_flat
        skip_binding['condition']['fmt_iface']=-1 #condition_fmt_iface_flat
        skip_bindings[bdx]=skip_binding

        # Second, create skipping SAF
        skipping_saf=SAFSkipping.copy() \
                                .target(target_buffer) \
                                .set_attribute("bindings",[target_buffer, \
                                                           target_fmt_iface_flat, \
                                                           condition_buffer, \
                                                           condition_fmt_iface_flat] \
                                              )\
                                .build("skipping_saf")

        saf_list.append(skipping_saf)

    [print(saf) for saf in saf_list]
    taxo_arch=genArch(buffer_stub_list, buffer_hierarchy, saf_list)

    return taxo_arch   