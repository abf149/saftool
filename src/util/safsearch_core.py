'''
from util import sparseloop_config_processor as sl_config, safinfer_io, safmodel_io
from solver.solve import Solver
from solver.build import build_taxonomic_arch_and_safs_from_bindings
from util.helper import info,warn,error
import util.helper as helper
import util.safsearch_io as safsearch_io
from util.notation.generators.rules import findAllInstancesPartiallyMatchingObjectAttributes
import util.notation.predicates as pr_
import saflib.microarchitecture.TaxoRegistry as tr_ # Initialize taxonomic registry (TODO: from files)
#from util.safinfer_io import sprettyprint_taxo_uarch
#from solver.build import get_buffer_hierarchy
import solver.model.build as build
import solver.model.solve as solve
import safinfer
import copy
'''
import search.taxonomic.build.component as bc_
from util.helper import info,warn,error

def build_taxonomic_search_space(arch, \
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
    safinfer_user_attributes, \
    characterization_path_list, \
    model_script_lib_list, \
    top_lvl_comp_cnt_sanity_limit=100, \
    comp_tree_depth_sanity_limit=100):
    
    info(":: Building taxonomic search-space...",also_stdout=True)
    per_comp_search_space=bc_.build_per_component_taxonomic_search_space(arch, \
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
                                                                         safinfer_user_attributes, \
                                                                         characterization_path_list, \
                                                                         model_script_lib_list, \
                                                                         top_lvl_comp_cnt_sanity_limit= \
                                                                            top_lvl_comp_cnt_sanity_limit, \
                                                                         comp_tree_depth_sanity_limit= \
                                                                            comp_tree_depth_sanity_limit)

    warn(":: => Done, building taxonomic search-space.",also_stdout=True)
    return per_comp_search_space