'''Library for constructing a SAF microrarchitecture inference problem'''
import util.sparseloop_config_processor as sl_config
import util.parse as pr_
from util.helper import info,warn,error

def get_sparseloop_arch_parameter_dict(arch):
    version_=arch['architecture']['version']
    root_=arch['architecture']['subtree']
    if len(root_) == 1:
        return root_[0]['attributes']
    elif len(root_) == 0:
        return {}
    else:
        # Can't support multiple architectures at this time
        assert(False)

def get_buffer_hierarchy(arch):
    return [buffer for buffer in list(sl_config.flatten_arch_wrapper(arch).keys()) if buffer != 'MAC']

def get_port_mappings_to_flattened_indices(arch,dtype_list,fmt_iface_bindings,user_attributes={}):
    # Extract buffer hierarchy
    buffer_hierarchy=get_buffer_hierarchy(arch)

    # Compute flattened port indices
    port_idx={buffer:{dtype:[0 \
                    for fmt_iface in fmt_iface_bindings[buffer][dtype]] \
                            for dtype in dtype_list} \
                                    for buffer in buffer_hierarchy}

    dense_fmt_iface_bindings=[]
    if len(user_attributes) > 0:
        dense_fmt_iface_bindings=pr_.parse_dense_fmt_iface_settings(user_attributes)

    for buffer in buffer_hierarchy:
        # buff0_dtype0_fmt_iface{0,1,2,...}, buff0_dtype1_fmt_iface{0,1,2,...}, 
        # ..., buff1_dtype0_fmt_iface{0,1,2,...}, ...
        idx=0
        for dtype in dtype_list:
            if not(len(dense_fmt_iface_bindings)>0 and \
                   buffer in dense_fmt_iface_bindings and \
                    dtype in dense_fmt_iface_bindings[buffer] and \
                        len(dense_fmt_iface_bindings[buffer][dtype])>len(port_idx[buffer][dtype])):
                for jdx in range(len(port_idx[buffer][dtype])):
                    port_idx[buffer][dtype][jdx]=idx
                    idx+=1
            else:
                port_idx[buffer][dtype]=[]
                for jdx in range(len(dense_fmt_iface_bindings[buffer][dtype])):
                    port_idx[buffer][dtype].append(idx)
                    idx+=1

    return port_idx