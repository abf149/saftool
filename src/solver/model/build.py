'''Build a SAFModel throughput inference problem'''
from util.helper import info, warn, error
from .build_support.build1 import build1_graph_representation
from .build_support.build2 import build2_system_of_relations
from .build_support.build3 import build3_simplify_system

def build_scale_inference_problem(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                  buffer_kept_dataspace_by_buffer,buff_dags,constraints=[]):

    info("Building scale inference problem...",also_stdout=True)

    problem_as_graph=build1_graph_representation(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                                 buffer_kept_dataspace_by_buffer,buff_dags,constraints)

    problem_as_system=build2_system_of_relations(problem_as_graph)

    simplified_system=build3_simplify_system(problem_as_system)

    info("=> Done, build.",also_stdout=True)