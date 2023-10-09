'''Export analytical model primitives'''

import export.export_support.modeling_backends.Accelergy as acc_
from util.helper import info,warn,error

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