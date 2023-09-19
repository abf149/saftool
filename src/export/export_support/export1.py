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

def exportPrimitiveObjectiveRepresentationToBackend(backend_rep, backend="accelergy"):
    info("-- Persisting primitive objective function in backend-compatible format...")

    if backend=="accelergy":
        acc_.exportAccelergyERTART(backend_rep)
    else:
        error("Invalid modeling backend",backend)
        info("Terminating.")     
        assert(False)   

    warn("-- => done, persisting")

def export1_backend_objective_models(abstract_analytical_models_dict, \
                                     primitive_models):
    warn("- Starting export of objective function models to modeling backend")

    backend_rep=getBackendPrimitiveObjectiveRepresentation(abstract_analytical_models_dict, \
                                                           primitive_models)

    exportPrimitiveObjectiveRepresentationToBackend(backend_rep)

    warn("- done, objective models backend export")
    return backend_rep