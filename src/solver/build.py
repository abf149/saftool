'''Library for constructing a SAF microrarchitecture inference problem'''
from saflib.architecture.taxo.Architecture import ArchitectureBase
from core.notation.microarchitecture import TopologyWrapper
import solver.build_support.action as ac_
import solver.build_support.arch as ar_
import solver.build_support.format as fm_
from core.helper import info,warn,error

def get_buffer_stubs_and_SAFs_from_bindings(arch, \
                                            fmt_iface_bindings, \
                                            action_bindings, \
                                            dtype_list, \
                                            user_attributes={}):
    # Generate buffer stubs and format SAFs
    buffer_stub_list, \
    saf_list = fm_.get_buffer_stubs_and_format_safs(arch, fmt_iface_bindings)
    saf_list = ac_.get_action_SAFs_from_action_bindings(arch, \
                                                        fmt_iface_bindings, \
                                                        action_bindings, \
                                                        dtype_list, \
                                                        saf_list, \
                                                        user_attributes=user_attributes)
    return buffer_stub_list, saf_list
def build_taxonomic_arch_and_safs_from_bindings(arch, \
                                                fmt_iface_bindings, \
                                                action_bindings, \
                                                dtype_list, \
                                                user_attributes={}):
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
                                                                         dtype_list, \
                                                                         user_attributes=user_attributes)
    return ArchitectureBase.copy() \
                           .topology(TopologyWrapper().components(buffer_stub_list)) \
                           .SAFs(saf_list) \
                           .buffers(ar_.get_buffer_hierarchy(arch)) \
                           .build()  