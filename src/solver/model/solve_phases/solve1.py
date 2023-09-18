'''Solve a simplified scale inference problem'''
import os
import re
from pyomo.environ import *
import sympy as sp
from util.helper import info,warn,error

def solve1_scale_inference_simplified_problem(final_symbols,final_symbol_types,final_constraints,yields):
    #print([x for x in final_constraints if "Eq" in x or "eq" in x])
    #print(final_constraints.index("eq"),final_constraints.index("ineq"))
    #print(final_constraints[final_constraints.index("eq")-1],final_constraints[final_constraints.index("eq")+1])

    info("- Solve phase 1: solve MINLP")

    os.environ['NEOS_EMAIL'] = 'abf149@mit.edu'

    # Create a model instance
    model = ConcreteModel()

    # Mapping symbols to more convenient names
    variable_mapping = {sym: f'x{i+1}' for i, sym in enumerate(final_symbols)}

    #print(variable_mapping)

    # Defining the variables based on their types
    for sym, sym_type in zip(final_symbols, final_symbol_types):
        var_name = variable_mapping[sym]
        #print(var_name)
        if sym_type == 'int':
            setattr(model, var_name, Var(within=Integers))
        elif sym_type == 'float':
            setattr(model, var_name, Var(within=NonNegativeReals))

    # Sort the symbols by length in descending order to ensure longer names are replaced first
    sorted_symbols = sorted(variable_mapping.keys(), key=len, reverse=True)

    # Process constraints
    for jdx,constraint in enumerate(final_constraints):
        # If the constraint is a regular inequality/equality:
        if 'in(' not in constraint and '|' not in constraint and '&' not in constraint:
            # Transform the constraint with the new variable names
            for original in sorted_symbols:
                mapped = variable_mapping[original]
                constraint = constraint.replace(original, f"model.{mapped}")
            constr_expr = eval(constraint)
            #print(constr_expr)
            setattr(model, f'constr_{str(jdx)}', Constraint(expr=constr_expr))

        # If the constraint specifies a variable to be in a set:
        elif 'in(' in constraint:
            match = re.search(r'in\(([^,]+), \{([^}]+)\}\)', constraint)
            if match:
                var, vals = match.groups()
                vals = set(map(int, vals.split(',')))
                max_val = max(vals)
                binary_vars = [Var(within=Binary) for _ in vals]
                idx=0
                for v, bin_var in zip(vals, binary_vars):
                    setattr(model, f'binVar_in_{jdx}_{idx}', bin_var)
                    #print(constraint,f'constr_{jdx}_{variable_mapping[var]}_{v}_upper')
                    setattr(model, f'constr_{jdx}_{variable_mapping[var]}_{v}_upper', Constraint(expr=getattr(model, variable_mapping[var]) - v <= max_val * (1 - bin_var)))
                    setattr(model, f'constr_{jdx}_{variable_mapping[var]}_{v}_lower', Constraint(expr=getattr(model, variable_mapping[var]) - v >= -max_val * (1 - bin_var)))
                    idx+=1
                #print(f'constr_sum_{var}')
                setattr(model, f'constr_{jdx}_sum_{variable_mapping[var]}', Constraint(expr=sum(bin_var for bin_var in binary_vars) == 1))

        # If the constraint specifies allowed combinations of variable values:
        elif '|' in constraint:
            or_parts = constraint.split('|')
            binary_or_vars = [Var(within=Binary) for _ in or_parts]

            for idx,bin_or_var in enumerate(binary_or_vars):
                setattr(model, f'binVar_or_{jdx}_{idx}', bin_or_var)

            M = 1000  # A sufficiently large number, adjust as needed

            for idx, part in enumerate(or_parts):
                and_parts = part.strip().split('&')
                binary_and_vars = [Var(within=Binary) for _ in and_parts]

                for kdx,bin_and_var in enumerate(binary_and_vars):
                    setattr(model, f'binVar_and_{jdx}_{idx}_{kdx}', bin_and_var)

                for j, subpart in enumerate(and_parts):
                    eq_match = re.search(r'Eq\(([^,]+), ([^\)]+)\)', subpart)
                    if eq_match:
                        var, val = eq_match.groups()
                        var_val = int(val)

                        # Upper and lower bound constraints to link binary variable
                        #print(constraint,f'link_{jdx}_and_{idx}_{j}_upper')
                        model.add_component(f'link_{jdx}_and_{idx}_{j}_upper', Constraint(expr=getattr(model, variable_mapping[var]) - var_val <= M * (1 - binary_and_vars[j])))
                        model.add_component(f'link_{jdx}_and_{idx}_{j}_lower', Constraint(expr=getattr(model, variable_mapping[var]) - var_val >= -M * (1 - binary_and_vars[j])))

                # Check if all conditions of the AND are true
                #print(constraint,f'constr_{jdx}_and_{idx}')
                model.add_component(f'constr_{jdx}_and_{idx}', Constraint(expr=sum(binary_and_vars) - len(and_parts) * binary_or_vars[idx] == 0))

            #print(constraint,f'constr_or_{jdx}')
            model.add_component(f'constr_or_{jdx}', Constraint(expr=sum(binary_or_vars) >= 1))

    # Objective function
    model.obj = Objective(expr=sum(getattr(model, variable_mapping[sym]) for sym in final_symbols), sense=minimize)

    # Solve the model
    solver_manager = SolverManagerFactory('neos')
    results = solver_manager.solve(model, opt='bonmin', tee=True, keepfiles=True)

    # Display results
    if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
        for original, mapped in variable_mapping.items():
            print(f"{original} = {getattr(model, mapped)()}")
        print(f"Objective value: {model.obj()}")
    else:
        print("No solution found!")

    info("- => done, solve phase 1.")