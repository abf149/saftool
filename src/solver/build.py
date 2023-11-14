'''Library for constructing a SAF microrarchitecture inference problem'''
from saflib.architecture.taxo.stub_primitives.BufferStub import BufferStub
from saflib.saf.FormatSAF import FormatSAF
from saflib.saf.SkippingSAF import SkippingSAF
from saflib.architecture.taxo.Architecture import ArchitectureBase
from util.notation.microarchitecture import TopologyWrapper
import util.sparseloop_config_processor as sl_config, copy

def get_buffer_hierarchy(arch):
    return [buffer for buffer in list(sl_config.flatten_arch_wrapper(arch).keys()) if buffer != 'MAC']
def get_port_mappings_to_flattened_indices(arch,dtype_list,fmt_iface_bindings):
    # Extract buffer hierarchy
    buffer_hierarchy=get_buffer_hierarchy(arch)

    # Compute flattened port indices
    port_idx={buffer:{dtype:[0 \
                    for fmt_iface in fmt_iface_bindings[buffer][dtype]] \
                            for dtype in dtype_list} \
                                    for buffer in buffer_hierarchy}

    for buffer in buffer_hierarchy:
        # buff0_dtype0_fmt_iface{0,1,2,...}, buff0_dtype1_fmt_iface{0,1,2,...}, 
        # ..., buff1_dtype0_fmt_iface{0,1,2,...}, ...
        idx=0
        for dtype in dtype_list:
            for jdx in range(len(port_idx[buffer][dtype])):
                port_idx[buffer][dtype][jdx]=idx
                idx+=1

    return port_idx

def get_buffer_stubs_and_format_safs(arch, fmt_iface_bindings, buffer_stub_list=[], saf_list=[]):
    buffer_stub_list=[]
    saf_list=[]
    buffer_hierarchy=get_buffer_hierarchy(arch)    
    for buffer in buffer_hierarchy:
        datatype_fmt_ifaces=fmt_iface_bindings[buffer]

        if sum([len(datatype_fmt_ifaces[dtype]) for dtype in datatype_fmt_ifaces])>0:
            fmt_saf=FormatSAF.copy() \
                             .target(buffer) \
                             .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree")

            buffer_stub=BufferStub.copy() \
                                  .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree") \
                                  .generate_ports("fibertree","fibertree")
            buffer_stub_list.append((buffer,buffer_stub))
            saf_list.append(("format_saf",fmt_saf))    
    return buffer_stub_list, saf_list
def get_skipping_SAFs_from_skip_bindings(arch, fmt_iface_bindings, skip_bindings, dtype_list, saf_list=[]):
    #print("\n\n\n\n")
    #print(fmt_iface_bindings)
    #print("\n\n\n\n")
    #print(skip_bindings)

    #assert(False)

    port_idx = get_port_mappings_to_flattened_indices(arch, \
                                                              dtype_list, \
                                                              fmt_iface_bindings \
                                                             )

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
        condition_fmt_iface_flat=port_idx[condition_buffer][condition_dtype][1] #condition_fmt_iface

        skip_binding['target']['fmt_iface']=-1 #target_fmt_iface_flat
        skip_binding['condition']['fmt_iface']=-1 #condition_fmt_iface_flat
        skip_bindings[bdx]=skip_binding

        # Second, create skipping SAF
        skipping_saf=SkippingSAF.copy() \
                                .target(target_buffer) \
                                .set_attribute("bindings",[target_buffer, \
                                                           target_fmt_iface_flat, \
                                                           condition_buffer, \
                                                           condition_fmt_iface_flat])
        if skip_binding["bidirectional"]:
            skipping_saf.set_attribute("direction","bidirectional")
        else:
            skipping_saf.set_attribute("direction","leader_follower")

        saf_list.append(("skipping_saf",skipping_saf))

    return saf_list
def get_buffer_stubs_and_SAFs_from_bindings(arch, fmt_iface_bindings, action_bindings, dtype_list):
    # Generate buffer stubs and format SAFs
    buffer_stub_list, \
    saf_list = get_buffer_stubs_and_format_safs(arch, fmt_iface_bindings)
    saf_list = get_skipping_SAFs_from_skip_bindings(arch, fmt_iface_bindings, action_bindings, dtype_list, saf_list)
    return buffer_stub_list, saf_list
def build_taxonomic_arch_and_safs_from_bindings(arch, fmt_iface_bindings, action_bindings, dtype_list):
    '''
    Generate taxonomic representation of topology and SAF optimizations\n\n

    Arguments:\n
    - arch -- Sparseloop architecture YAML object\n
    - fmt_iface_bindings -- inferred bindings of rank representation format parsing interfaces to buffer stubs\n
        - Example:\n\n
        
        {'BackingStorage': \n
            {'Outputs': [], \n
             'Inputs': [{'format': 'UOP', 'fiber_layout': [['!0']]}, \n
                        ...\n
                        {'format': 'UOP', 'fiber_layout': [['R', 'E']]}\n
                       ],\n
             'Weights': ...},\n
         'iact_spad': ...,\n
         ...,\n
         'MAC': {'Outputs': [], 'Inputs': [], 'Weights': []}\n
        }\n\n

    - skip_bindings -- inferred bindings of skipping SAFs to buffers\n
        - Example:\n\n

        [
            {'type': 'skipping', \n
             'bidirectional': False, \n
             'target': {'buffer': 'weight_spad', \n
                        'dtype': 'Weights'\n
                       }, 
             'condition': {'buffer': 'iact_spad', \n
                           'dtype': 'Inputs' \n
                          }, 
             'must_discard': False, \n
             'must_post_gate': False\n
            }\n
        ]\n\n
    - dtype_list -- inferred datatypes in the tensor problems addressable by this accelerator\n
        - Example: ['Weights', 'Outputs', 'Inputs']\n\n

    Returns:\n
    - Taxonomic "Architecture" object with SAF annotations and netless topology consisting of buffer stubs
    ''' 
    buffer_stub_list, saf_list = get_buffer_stubs_and_SAFs_from_bindings(arch, \
                                                                         fmt_iface_bindings, \
                                                                         action_bindings, \
                                                                         dtype_list)
    return ArchitectureBase.copy() \
                           .topology(TopologyWrapper().components(buffer_stub_list)) \
                           .SAFs(saf_list) \
                           .buffers(get_buffer_hierarchy(arch)) \
                           .build()  