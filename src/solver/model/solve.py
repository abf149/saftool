'''Build a SAFModel throughput inference problem'''
from util.helper import info,warn,error
from solver.model.solve_phases.solve1 import solve1_scale_inference

def solve(sclp):
    warn("Solving scale inference problem.",also_stdout=True)
    abstract_analytical_models_dict=solve1_scale_inference(sclp)
    warn("=> done, solve.",also_stdout=True)
    return abstract_analytical_models_dict