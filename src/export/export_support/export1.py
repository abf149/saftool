'''Export analytical model primitives'''

import export.export_support.modeling_backends.Accelergy as acc_
from util.helper import info,warn,error

def getBackendPrimitiveObjectiveRepresentation(abstract_analytical_models_dict, \
                                               primitive_models, backend="accelergy"):
    '''Get a backend-compatible representation of all 
       primitives' objective function values'''
    info("-- Generating backend-compatible representation of primitive objective function...")
    info("--- modeling backend =",backend)

    res={}
    if backend=="accelergy":
        res=acc_.getAccelergyTables(abstract_analytical_models_dict,primitive_models)
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

    warn("-- => done, persisting")

    return dump_fn

def installToBackend(dump_fn,backend='accelergy'):
    info("-- Copying primitive objective functions to backend install dir...")

    install_path=None
    if backend=="accelergy":
        install_path=acc_.installERTART(dump_fn)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)   

    warn("-- => done, installing")
    return install_path

def export1_backend_objective_models(abstract_analytical_models_dict, \
                                     primitive_models):
    warn("- Starting export of objective function models to modeling backend")

    backend_rep=getBackendPrimitiveObjectiveRepresentation(abstract_analytical_models_dict, \
                                                           primitive_models)

    dump_fn=exportPrimitiveObjectiveRepresentation(backend_rep)

    install_fn=installToBackend(dump_fn)

    warn("- done, objective models backend export")
    return backend_rep