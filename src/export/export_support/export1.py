'''Export analytical model primitives'''

import export.export_support.modeling_backends.Accelergy as acc_
from core.helper import info,warn,error

def getBackendPrimitiveLibraryRepresentation(analytical_model_classes_dict, \
                                             analytical_model_actions_dict, \
                                             backend="accelergy", \
                                             backend_args={}):
    '''Get a backend-compatible reprsentation of all
       primitive classes'''
    info("-- Generating backend-compatible representation of primitive classes...")
    info("--- modeling backend =",backend)

    res={}
    if backend=="accelergy":
        res=acc_.getAccelergyPrimitivesLibrary(analytical_model_classes_dict, \
                                               analytical_model_actions_dict, \
                                               backend_args=backend_args)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")
        assert(False)

    warn("-- => done, generating backend primitive classes data structure")
    return res

def getBackendComponentLibraryRepresentation(analytical_component_model_classes_dict, \
                                             analytical_primitive_model_classes_dict, \
                                             analytical_component_model_actions_dict, \
                                             analytical_primitive_model_actions_dict, \
                                             abstract_analytical_primitive_models_dict, \
                                             abstract_analytical_component_models_dict, \
                                             component_energy_action_tree, \
                                             backend="accelergy", \
                                             backend_args={}):
    
    '''Get a backend-compatible reprsentation of all component classes'''
    
    info("-- Generating backend-compatible representation of component classes...")
    info("--- modeling backend =",backend)

    res={}
    if backend=="accelergy":
        res=acc_.getAccelergyComponentsLibrary(analytical_component_model_classes_dict, \
                                               analytical_primitive_model_classes_dict, \
                                               analytical_component_model_actions_dict, \
                                               abstract_analytical_primitive_models_dict, \
                                               abstract_analytical_component_models_dict, \
                                               component_energy_action_tree, \
                                               backend_args=backend_args)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")
        assert(False)

    warn("-- => done, generating backend component classes data structure")
    return res

def getBackendBufferLibraryRepresentation(flat_comp_dict, \
                                          flat_arch, \
                                          backend_comp_lib_rep, \
                                          analytical_component_model_classes_dict, \
                                          analytical_primitive_model_classes_dict, \
                                          analytical_component_model_actions_dict, \
                                          analytical_primitive_model_actions_dict, \
                                          abstract_analytical_primitive_models_dict, \
                                          abstract_analytical_component_models_dict, \
                                          buffer_action_tree, \
                                          backend="accelergy", \
                                          backend_args={}):

    '''Get a backend-compatible reprsentation of all buffers which interact with microarchitecture models'''

    info("-- Generating backend-compatible representation of buffer models augmented with microarchitecture models...")
    info("--- modeling backend =",backend)

    res={}
    if backend=="accelergy":
        res=acc_.getAccelergyBufferLibrary(flat_arch, \
                                           flat_comp_dict, \
                                           backend_comp_lib_rep, \
                                           analytical_component_model_classes_dict, \
                                           analytical_primitive_model_classes_dict, \
                                           analytical_component_model_actions_dict, \
                                           abstract_analytical_primitive_models_dict, \
                                           abstract_analytical_component_models_dict, \
                                           buffer_action_tree, \
                                           backend_args=backend_args)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")
        assert(False)

    warn("-- => done, generating backend buffer model data structure")
    return res

def getBackendPrimitiveObjectiveRepresentation(abstract_analytical_models_dict, \
                                               primitive_models, backend="accelergy", \
                                               backend_args={}):
    '''Get a backend-compatible representation of all 
       primitives' objective function values'''
    info("-- Generating backend-compatible representation of primitive objective function...")
    info("--- modeling backend =",backend)

    res={}
    if backend=="accelergy":
        res=acc_.getAccelergyTables(abstract_analytical_models_dict,primitive_models,backend_args=backend_args)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")
        assert(False)

    warn("-- => done, generating backend primitive objective data structure")
    return res

def getBackendArchTransformation(arch, \
                                 backend_buffer_lib_rep, \
                                 backend="accelergy", \
                                 backend_args={}):
    '''In a backend-compatible fashion, transform the input arch to include
       new buffer models with integrated SAF microarchitecture models'''
    
    info("-- Generating backend-compatible representation of arch...")
    info("--- modeling backend =",backend)

    res={}
    if backend=="accelergy":
        res=acc_.getAccelergyBackendArchTransformation(arch,backend_buffer_lib_rep, \
                                                       backend,backend_args=backend_args)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")
        assert(False)

    warn("-- => done, generating backend arch datastructure")
    return res

def exportPrimitiveObjectiveRepresentation(backend_rep, backend="accelergy"):
    info("-- Persisting primitive objective functions in backend-compatible format...")

    dump_fn=None
    if backend=="accelergy":
        dump_fn=acc_.exportAccelergyERTART(backend_rep)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)   

    warn("-- => done, persisting primitive objective functions")
    return dump_fn

def exportPrimitiveLibraryRepresentation(backend_lib_rep, backend="accelergy"):
    info("-- Persisting primitive library in backend-compatible format...")

    dump_fn=None
    if backend=="accelergy":
        dump_fn=acc_.exportAccelergyPrimitivesLib(backend_lib_rep)
        #dump_fn=acc_.exportAccelergyERTART(backend_rep)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)  

    warn("-- => done, persisting primitive library")
    return dump_fn

def exportComponentLibraryRepresentation(backend_lib_rep, \
                                         backend_buffer_lib_rep, \
                                         backend="accelergy", backend_args={}):
    info("-- Persisting component library in backend-compatible format...")

    dump_fn=None
    if backend=="accelergy":
        component_install_dir=None
        if 'comp_out_path' in backend_args:
            component_install_dir=backend_args['comp_out_path']
        component_single_file=True
        if 'component_single_file' in backend_args:
            component_single_file=backend_args['component_single_file']

        dump_fn=acc_.exportAccelergyComponentsLib(backend_lib_rep, \
                                                  backend_buffer_lib_rep, \
                                                  component_install_dir, \
                                                  component_single_file)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)  

    warn("-- => done, persisting component library")
    return dump_fn

def exportAugmentedArchRepresentation(backend_arch_rep, \
                                      backend='accelergy', \
                                      backend_args={}):
    info("-- Persisting transformed arch into backend-compatible format...")

    dump_fn=None
    if backend=="accelergy":
        arch_install_filename=None
        if 'arch_out_path' in backend_args:
            arch_install_filename=backend_args['arch_out_path']

        dump_fn=acc_.exportAccelergyArchSpec(backend_arch_rep, \
                                             arch_install_filename)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)  

    warn("-- => done, persisting transformed arch")
    return dump_fn    


def installObjectiveToBackend(dump_fn,backend='accelergy'):
    info("-- Copying primitive objective functions to backend install dir...")

    install_path=None
    if backend=="accelergy":
        install_path=acc_.installERTART(dump_fn)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)   

    warn("-- => done, installing primitive objective functions")
    return install_path

def installPrimitiveLibToBackend(lib_dump_fn, backend='accelergy'):
    info("-- Copying primitive library to backend install dir...")

    install_path=None
    if backend=="accelergy":
        install_path=acc_.installPrimitivesLib(lib_dump_fn)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)   

    warn("-- => done, installing primitive library")
    return install_path

def export1_backend_objective_models(abstract_analytical_models_dict, \
                                     primitive_models, \
                                     backend='accelergy', \
                                     backend_args={}):
    warn("- Starting export of objective function models to modeling backend")

    backend_obj_rep=getBackendPrimitiveObjectiveRepresentation(abstract_analytical_models_dict, \
                                                               primitive_models, \
                                                               backend=backend, \
                                                               backend_args=backend_args)

    obj_dump_fn=exportPrimitiveObjectiveRepresentation(backend_obj_rep, \
                                                       backend=backend)

    obj_install_fn=installObjectiveToBackend(obj_dump_fn, \
                                             backend=backend)

    warn("- done, objective models backend export")
    return backend_obj_rep

def export1_backend_primitive_lib(analytical_model_classes_dict, \
                                  analytical_model_actions_dict, \
                                  backend='accelergy', \
                                  backend_args={}):
    warn("- Starting export of primitive library to modeling backend")
    backend_lib_rep=getBackendPrimitiveLibraryRepresentation(analytical_model_classes_dict, \
                                                             analytical_model_actions_dict, \
                                                             backend=backend, \
                                                             backend_args=backend_args)    
    lib_dump_fn=exportPrimitiveLibraryRepresentation(backend_lib_rep, \
                                                     backend=backend)
    lib_install_fn=installPrimitiveLibToBackend(lib_dump_fn, \
                                                backend=backend)
    warn("- done, primitive library backend export")
    return backend_lib_rep

def export1_backend_primitive_lib_objective_models(scale_problem, \
                                                   analytical_model_classes_dict, \
                                                   analytical_model_actions_dict, \
                                                   abstract_analytical_models_dict, \
                                                   backend='accelergy', \
                                                   backend_args={}):
    
    backend_obj_rep=export1_backend_objective_models(abstract_analytical_models_dict, \
                                                     scale_problem['primitive_models'], \
                                                     backend=backend, \
                                                     backend_args=backend_args)
    
    backend_lib_rep=export1_backend_primitive_lib(analytical_model_classes_dict, \
                                                  analytical_model_actions_dict, \
                                                  backend=backend, \
                                                  backend_args=backend_args)
    
    return backend_obj_rep, backend_lib_rep

def flatten_component_lib_list(comp_in):
    info("-- Flatting input component libraries...")
    info("---",len(comp_in),"libs...")
    flat_comp_dict={}

    for idx,comp_lib in enumerate(comp_in):
        comp_lib_breakout=comp_lib['compound_components']
        info("---- lib",str(idx),": version",comp_lib_breakout['version'],",",len(comp_lib_breakout['classes']),"classes")
        class_display_list=[]
        for comp_struct in comp_lib_breakout['classes']:
            comp_name=comp_struct['name']
            class_display_list.append(comp_name)
            if comp_name in flat_comp_dict:
                error("---",comp_name,"occurs >1 times in input component libs.",also_stdout=True)
                error("--- Existing component:")
                error(flat_comp_dict[comp_name])
                error("--- New component:")
                error(comp_struct)
                info("Terminating.")
                assert(False)
            flat_comp_dict[comp_name]=comp_struct
        info("----- lib classes:",class_display_list)

    info("---- Final flattened class list:",list(flat_comp_dict.keys()))
    info("-- => Done, flattening input component libraries.")
    return flat_comp_dict

def export2_backend_component_lib(comp_in, \
                                  scale_problem, \
                                  analytical_primitive_model_classes_dict, \
                                  analytical_component_model_classes_dict, \
                                  analytical_primitive_model_actions_dict, \
                                  analytical_component_model_actions_dict, \
                                  abstract_analytical_primitive_models_dict, \
                                  abstract_analytical_component_models_dict, \
                                  buffer_action_tree, \
                                  backend='accelergy', \
                                  backend_args={}):
        
    warn("- Starting export of component library to modeling backend")
    component_energy_action_tree=scale_problem["component_energy_action_tree"]
    flat_arch=scale_problem["flat_arch"]
    flat_comp_dict=flatten_component_lib_list(comp_in)

    backend_comp_lib_rep=getBackendComponentLibraryRepresentation(analytical_component_model_classes_dict, \
                                                                  analytical_primitive_model_classes_dict, \
                                                                  analytical_component_model_actions_dict, \
                                                                  analytical_primitive_model_actions_dict, \
                                                                  abstract_analytical_primitive_models_dict, \
                                                                  abstract_analytical_component_models_dict, \
                                                                  component_energy_action_tree, \
                                                                  backend=backend, \
                                                                  backend_args=backend_args)

    backend_buffer_lib_rep=getBackendBufferLibraryRepresentation(flat_comp_dict, \
                                                                 flat_arch, \
                                                                 backend_comp_lib_rep, \
                                                                 analytical_component_model_classes_dict, \
                                                                 analytical_primitive_model_classes_dict, \
                                                                 analytical_component_model_actions_dict, \
                                                                 analytical_primitive_model_actions_dict, \
                                                                 abstract_analytical_primitive_models_dict, \
                                                                 abstract_analytical_component_models_dict, \
                                                                 buffer_action_tree, \
                                                                 backend=backend, \
                                                                 backend_args=backend_args)

    lib_dump_fn=exportComponentLibraryRepresentation(backend_comp_lib_rep, \
                                                     backend_buffer_lib_rep, \
                                                     backend=backend, \
                                                     backend_args=backend_args)
    
    #lib_install_fn=installComponentLibToWorkingDir(lib_dump_fn, \
    #                                                backend=backend)
    warn("- done, component library backend export")

    return backend_comp_lib_rep,backend_buffer_lib_rep

def export3_backend_arch_update(backend_buffer_lib_rep, \
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
                                backend_args={}):
        
    warn("- Starting transformation of input model arch into microarchitecture-augmented arch")
    
    #component_energy_action_tree=scale_problem["component_energy_action_tree"]
    #flat_arch=scale_problem["flat_arch"]
    arch=scale_problem["arch"]
    #flat_comp_dict=flatten_component_lib_list(comp_in)


    backend_arch_rep=getBackendArchTransformation(arch, \
                                                  backend_buffer_lib_rep, \
                                                  backend="accelergy", \
                                                  backend_args=backend_args)

    lib_dump_fn=exportAugmentedArchRepresentation(backend_arch_rep, \
                                                  backend=backend, \
                                                  backend_args=backend_args)
    

    warn("- done, microarchitecture-augmented arch")

    return backend_arch_rep