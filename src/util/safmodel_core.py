'''SAFmodel core library - build and solve SAF model synthesis problem 
                           from microarchitecture & Sparseloop problem description'''
import util.sparseloop_config_processor as sl_config
#from util.safinfer_io import sprettyprint_taxo_uarch
#from solver.build import get_buffer_hierarchy
import solver.model.build as build
import solver.model.solve as solve
#import util.helper as helper
from util.helper import info,warn,error

def update_user_attribute(user_attributes,field,source_dict,default_source='defaults'):
    if field in source_dict:
        warn('Updating',field,'=',source_dict[field],'from',default_source,'to',field,"=", \
             user_attributes['field'],'from user-provided attributes')
    else:
        warn('Setting',field,"=",user_attributes[field],'from user-provided attributes')

    return user_attributes

def default_user_attribute(user_attributes,field,source_dict,default_source='defaults'):
    if field not in source_dict:
        error('Required global setting',field,'is not specified by user or in',default_source,also_stdout=True)
        info('Terminating.',also_stdout=True)
        assert(False)
    warn('Setting',field,"=",source_dict[field],'from',default_source)
    user_attributes[field]=source_dict[field]
    return user_attributes

def update_or_default_user_attribute(user_attributes,field,source_dict,default_source='defaults'):
    if field in user_attributes:
        user_attributes=update_user_attribute(user_attributes,field,source_dict,default_source)
    else:
        user_attributes=default_user_attribute(user_attributes,field,source_dict,default_source)

    return user_attributes

def complete_user_attributes(user_attributes,system_attributes):
    user_attributes=update_or_default_user_attribute(user_attributes,'technology',system_attributes,'arch.yaml')
    user_attributes=update_or_default_user_attribute(user_attributes,'clock_period',system_attributes,'arch.yaml')
    user_attributes=update_or_default_user_attribute(user_attributes,'constraints',{'constraints':[]},'defaults')
    return user_attributes

def build_scale_inference_problem(arch, sparseopts, taxo_uarch, user_attributes={}):

    fmt_iface_bindings, \
    skip_bindings, \
    dtype_list, \
    buff_dags, \
    buffer_kept_dataspace_by_buffer = sl_config.compute_fixed_arch_bindings(arch,sparseopts)

    system_attributes = sl_config.get_sparseloop_arch_parameter_dict(arch)

    user_attributes = complete_user_attributes(user_attributes,system_attributes)

    return build.build_scale_inference_problem(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                               buffer_kept_dataspace_by_buffer,buff_dags,user_attributes=user_attributes)

def solve_scale_inference_problem(scale_prob):
    return solve.solve(scale_prob)