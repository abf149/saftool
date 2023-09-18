'''SAFmodel core library - build and solve SAF model synthesis problem 
                           from microarchitecture & Sparseloop problem description'''
import util.sparseloop_config_processor as sl_config
#from util.safinfer_io import sprettyprint_taxo_uarch
#from solver.build import get_buffer_hierarchy
import solver.model.build as build
#import solver.model.solve as solve
#import util.helper as helper

def build_scale_inference_problem(arch, sparseopts, taxo_uarch, constraints=[]):

    fmt_iface_bindings, \
    skip_bindings, \
    dtype_list, \
    buff_dags, \
    buffer_kept_dataspace_by_buffer = sl_config.compute_fixed_arch_bindings(arch,sparseopts)

    return build.build_scale_inference_problem(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                               buffer_kept_dataspace_by_buffer,buff_dags,constraints=constraints)


