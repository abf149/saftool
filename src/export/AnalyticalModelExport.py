'''Export components and primitives as analytical models i.e. Accelergy models'''
from .export_support.export1 import export1_backend_objective_models
from util.helper import info,warn,error

def export_backend_modeling_suite(abstract_analytical_models_dict,scale_problem):
    warn("Exporting backend modeling suite.",also_stdout=True)

    backend_rep=export1_backend_objective_models(abstract_analytical_models_dict, \
                                                 scale_problem['primitive_models'])

    warn("=> done, export modeling suite.",also_stdout=True)
    return backend_rep
    

