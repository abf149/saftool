from util.parse import extract_dtypes
from util.dense_bindings import flatten_arch_wrapper
from util.sparse_bindings_reconfigurable import compute_reconfigurable_arch_bindings
import util.bind_support.action as ac_, \
       util.bind_support.format as fm_
from util.helper import info,warn,error

def compute_fixed_arch_bindings(arch,sparseopts,user_attributes={}):
    skip_bindings=[]
    dtype_list=extract_dtypes(sparseopts)
    fmt_iface_bindings,buff_dags,buffer_kept_dataspace_by_buffer = \
        fm_.bind_format_iface_to_fixed_arch(arch, sparseopts, dtype_list)
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