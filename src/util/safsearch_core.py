from util import sparseloop_config_processor as sl_config, safinfer_io, safmodel_io
from solver.solve import Solver
from solver.build import build_taxonomic_arch_and_safs_from_bindings
from util.helper import info,warn,error
import saflib.microarchitecture.TaxoRegistry as tr_ # Initialize taxonomic registry (TODO: from files)
#from util.safinfer_io import sprettyprint_taxo_uarch
#from solver.build import get_buffer_hierarchy
import solver.model.build as build
import solver.model.solve as solve
#import util.helper as helper

def search_loop(arch, \
    mapping, \
    prob, \
    sparseopts, \
    reconfigurable_arch, \
    bind_out_path, \
    topo_out_path, \
    saflib_path, \
    do_logging,\
    log_fn, \
    taxo_script_lib_list, \
    taxo_uarch, \
    comp_in, \
    arch_out_path, \
    comp_out_path, \
    user_attributes, \
    characterization_path_list, \
    model_script_lib_list):
    pass