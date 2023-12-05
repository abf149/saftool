'''Export components and primitives as analytical models i.e. Accelergy models'''
from .export_support.export1 import export1_backend_primitive_lib_objective_models, \
                                    export2_backend_component_lib, \
                                    export3_backend_arch_update
from core.helper import info,warn,error

def export_backend_modeling_suite(comp_in, \
                                  analytical_primitive_model_classes_dict, \
                                  analytical_primitive_model_actions_dict, \
                                  abstract_analytical_primitive_models_dict, \
                                  analytical_component_model_classes_dict, \
                                  analytical_component_model_actions_dict, \
                                  abstract_analytical_component_models_dict, \
                                  scale_problem, \
                                  backend_args={}):
    warn("Exporting backend modeling suite.",also_stdout=True)

    buffer_action_tree=scale_problem["buffer_action_tree"]

    backend_obj_rep, backend_prim_lib_rep= \
        export1_backend_primitive_lib_objective_models(scale_problem, \
                                                       analytical_primitive_model_classes_dict, \
                                                       analytical_primitive_model_actions_dict, \
                                                       abstract_analytical_primitive_models_dict, \
                                                       backend='accelergy', \
                                                       backend_args=backend_args)

    backend_comp_lib_rep, backend_buffer_lib_rep= \
        export2_backend_component_lib(comp_in, \
                                      scale_problem, \
                                      analytical_primitive_model_classes_dict, \
                                      analytical_component_model_classes_dict, \
                                      analytical_primitive_model_actions_dict, \
                                      analytical_component_model_actions_dict, \
                                      abstract_analytical_primitive_models_dict, \
                                      abstract_analytical_component_models_dict, \
                                      buffer_action_tree, \
                                      backend='accelergy', \
                                      backend_args=backend_args)

    backend_arch_rep = \
        export3_backend_arch_update(backend_buffer_lib_rep, \
                                    comp_in, \
                                    scale_problem, \
                                    analytical_primitive_model_classes_dict, \
                                    analytical_component_model_classes_dict, \
                                    analytical_primitive_model_actions_dict, \
                                    analytical_component_model_actions_dict, \
                                    abstract_analytical_primitive_models_dict, \
                                    abstract_analytical_component_models_dict, \
                                    buffer_action_tree, \
                                    backend='accelergy', \
                                    backend_args=backend_args)

    warn("=> done, export modeling suite.",also_stdout=True)
    return backend_obj_rep, backend_prim_lib_rep, backend_comp_lib_rep, backend_buffer_lib_rep
    

