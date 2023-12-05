from core.parse import extract_dtypes
from core.dense_bindings import flatten_arch_wrapper
from core.sparse_bindings_reconfigurable import compute_reconfigurable_arch_bindings
import core.bind_support.action as ac_, \
       core.bind_support.format as fm_
from core.helper import info,warn,error

def compute_fixed_arch_bindings(arch,sparseopts,user_attributes={}):
    skip_bindings=[]
    dtype_list=extract_dtypes(sparseopts,user_attributes)

    fmt_iface_bindings,buff_dags,buffer_kept_dataspace_by_buffer = \
        fm_.bind_format_iface_to_fixed_arch(arch, sparseopts, dtype_list, user_attributes)
    dtype_buffer_list=transpose_bindings(fmt_iface_bindings)
    action_bindings=ac_.compute_action_bindings(sparseopts, fmt_iface_bindings, dtype_buffer_list, user_attributes)

    return fmt_iface_bindings, action_bindings, dtype_list, buff_dags, buffer_kept_dataspace_by_buffer

# Get buffer list for each datatype
def transpose_bindings(fmt_iface_bindings):
    transposed_bindings = {}

    for buffer, data in fmt_iface_bindings.items():
        for dtype in data.keys():
            if dtype not in transposed_bindings:
                transposed_bindings[dtype] = []
            transposed_bindings[dtype].append(buffer)

    return transposed_bindings