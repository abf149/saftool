'''Export components and primitives as analytical models i.e. Accelergy models'''
from .export_support.export1 import export1_backend_primitive_lib_objective_models
from util.helper import info,warn,error

def export_backend_modeling_suite(analytical_model_classes_dict, \
                                  analytical_model_actions_dict, \
                                  abstract_analytical_models_dict, \
                                  scale_problem):
    warn("Exporting backend modeling suite.",also_stdout=True)

    backend_obj_rep, backend_lib_rep= \
        export1_backend_primitive_lib_objective_models(scale_problem, \
                                                       analytical_model_classes_dict, \
                                                       analytical_model_actions_dict, \
                                                       abstract_analytical_models_dict, \
                                                       backend='accelergy')

    warn("=> done, export modeling suite.",also_stdout=True)
    return backend_obj_rep, backend_lib_rep
    

