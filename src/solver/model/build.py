'''Build a SAFModel throughput inference problem'''
from util.helper import info, warn, error
from .build_support.build1 import build1_graph_representation
from .build_support.build2 import build2_system_of_relations
from .build_support.build3 import build3_simplify_system

def build_scale_inference_problem(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                  buffer_kept_dataspace_by_buffer,buff_dags,user_attributes=None):

    warn("Building scale inference problem...",also_stdout=True)

    if (user_attributes is None) or ('clock_period' not in user_attributes) or \
        ('constraints' not in user_attributes):
        error('User attributes must at least have a \'clock_period\' key and a constraints key with an empty list as value', \
              also_stdout=True)
        info('Terminating.')
        assert(False)

    constraints=user_attributes['constraints']
    problem_as_graph=build1_graph_representation(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                                 buffer_kept_dataspace_by_buffer,buff_dags,constraints)

    problem_as_system=build2_system_of_relations(problem_as_graph,user_attributes,fmt_iface_bindings,dtype_list)

    simplified_system=build3_simplify_system(problem_as_system)

    simplified_system['user_attributes']=user_attributes

    warn("=> Done, build.",also_stdout=True)

    return simplified_system