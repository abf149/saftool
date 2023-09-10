'''Build a SAFModel throughput inference problem'''
from solver.build import get_buffer_hierarchy
import util.sparseloop_config_processor as sl_config
from util.taxonomy.designelement import Architecture

import solver.model.build_support.abstraction as ab, solver.model.build_support.scale as sc, solver.model.build_support.relations as rn

import solver.model.solve_phases.solve1 as solve1

def solve(sclp):
    rlns=sclp['reln_list']
    port_list=sclp['port_list']
    net_list=sclp['net_list']
    out_port_net_dict=sclp['out_port_net_dict']

    transitive_closure_relns = \
           solve1.solve1_transitive_closure_dfs(port_list,net_list,out_port_net_dict)