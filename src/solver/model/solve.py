'''Build a SAFModel throughput inference problem'''
from util.helper import info,warn,error
from solver.model.solve_phases.solve1 import solve1_scale_inference_simplified_problem

def solve(sclp):
    warn("Solving scale inference problem.",also_stdout=True)
    simplified_symbols=sclp["simplified_symbols"]
    simplified_symbol_types=sclp["simplified_symbol_types"]
    simplified_constraints=sclp["simplified_constraints"]
    yields=sclp["yields"]
    solve1_scale_inference_simplified_problem(simplified_symbols, \
                                              simplified_symbol_types, \
                                              simplified_constraints, \
                                              yields)
    warn("=> done, solve.",also_stdout=True)