import os
os.environ['NEOS_EMAIL'] = 'abf149@mit.edu'

from pyomo.environ import *

# Create a model instance
model = ConcreteModel()

# Define the sets
x1_set = [1, 4, 7]
x2_set = [4, 8, 10]
comb_set = [(1, 4), (4, 10), (7, 8)]

# Define the variables
model.x1 = Var(within=Integers, bounds=(0, 10))
model.x2 = Var(within=Integers, bounds=(0, 15))
model.x3 = Var(within=NonNegativeReals, bounds=(0, 20))

model.y1 = Var(x1_set, within=Binary)
model.y2 = Var(x2_set, within=Binary)

# Set membership constraints using Big-M
M = 11  # Large enough to cover the domain of x1
for value in x1_set:
    model.add_component(f'constr_x1_upper_{value}', Constraint(expr=model.x1 - value <= M * (1 - model.y1[value])))
    model.add_component(f'constr_x1_lower_{value}', Constraint(expr=model.x1 - value >= -M * (1 - model.y1[value])))
model.y1_sum = model.Constraint(expr=sum(model.y1[value] for value in x1_set) == 1)

M = 16  # Large enough to cover the domain of x2
for value in x2_set:
    model.add_component(f'constr_x2_upper_{value}', Constraint(expr=model.x2 - value <= M * (1 - model.y2[value])))
    model.add_component(f'constr_x2_lower_{value}', Constraint(expr=model.x2 - value >= -M * (1 - model.y2[value])))
model.y2_sum = Constraint(expr=sum(model.y2[value] for value in x2_set) == 1)

# Combination constraint
model.comb_constr = Constraint(expr=sum(model.y1[i]*model.y2[j] for i, j in comb_set) >= 1)

# Objective function
model.obj = Objective(expr=model.x1**2 + model.x2**2 + model.x3**2 - 10*model.x1 - 5*model.x2 - 3*model.x3 + 20, sense=minimize)

# Use the NEOS server to solve the model with Bonmin as the solver
solver_manager = SolverManagerFactory('neos')
results = solver_manager.solve(model, opt='bonmin')

# Print results
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print(f"Optimal solution: x1 = {model.x1()}, x2 = {model.x2()}, x3 = {model.x3()}")
    print(f"Objective value: {model.obj()}")

    # Printing y1 and y2 values
    y1_values = [model.y1[i]() for i in model.y1]
    y2_values = [model.y2[i]() for i in model.y2]
    print(f"y1 values: {y1_values}")
    print(f"y2 values: {y2_values}")

else:
    print("No solution found!")

