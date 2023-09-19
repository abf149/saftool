from saflib.microarchitecture.taxo.skipping.IntersectionLeaderFollower import IntersectionLeaderFollower,buildIntersectionLeaderFollower
from saflib.microarchitecture.model.skipping.IntersectionLeaderFollower import IntersectionLeaderFollowerModel
import sympy as sp

import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('pyomo')
logger.setLevel(logging.DEBUG)

isectBuilder=buildIntersectionLeaderFollower("C","none")
isect=isectBuilder.build("TestIntersection")
isectModel=IntersectionLeaderFollowerModel.copy() \
                                .from_taxo_obj(isect) \
                                .build_symbols_constraints_objectives_attributes("asdf")

symbols, \
symbol_types, \
constraints, \
energy_objectives, \
area_objectives, \
yields = isectModel.get_scale_inference_problem()

constraints.append('asdf.TestIntersection.md_in_leader_rw == 2')
constraints.append('asdf.TestIntersection.md_in_leader_cr >= 4')
constraints.append('asdf.TestIntersection.md_in_leader_pr >= 2')
constraints.append('asdf.TestIntersection.md_in_leader_ww >= 1')
#constraints.append('asdf.TestIntersection.md_in_leader_pw >= 1')
constraints.append('asdf.TestIntersection.md_in_leader_nc >= 8')
constraints.append('asdf.TestIntersection.md_out_rw == 2')
constraints.append('asdf.TestIntersection.md_out_pr >= 2')
constraints.append('asdf.TestIntersection.md_out_cr >= 4')
constraints.append('asdf.TestIntersection.md_out_ww >= 1')
#constraints.append('asdf.TestIntersection.md_out_pw >= 1')
constraints.append('asdf.TestIntersection.md_out_nc >= 8')

#print(symbols)
#print(symbol_types)

#assert(False)

# Replace periods with double-underscores
modified_symbols = [s.replace('.', '__') for s in symbols]
modified_constraints = [c.replace('.', '__') for c in constraints]

# Convert modified symbols into sympy symbols
sympy_symbols = {s: sp.Symbol(s) for s in modified_symbols}

def convert_to_sympy_expr(constraint, symbols_dict):
    # Handle Piecewise expressions without splitting
    if 'Piecewise' in constraint:
        return sp.sympify(constraint, locals=symbols_dict)
    
    if '==' in constraint:
        lhs, rhs = constraint.split('==')
        return sp.Eq(sp.sympify(lhs.strip(), locals=symbols_dict), sp.sympify(rhs.strip(), locals=symbols_dict))
    
    return sp.sympify(constraint, locals=symbols_dict)

# Convert the modified constraints into Sympy expressions.
sympy_constraints = [convert_to_sympy_expr(c, sympy_symbols) for c in modified_constraints]

# Extract and use the equality constraints to substitute and reduce the number of symbols.
equalities = [c for c in sympy_constraints if isinstance(c, sp.Eq)]
others = [c for c in sympy_constraints if not isinstance(c, sp.Eq)]

substitutions = {}
for eq in equalities:
    substitutions[eq.lhs] = eq.rhs

simplified_constraints = []
for c in others:
    if isinstance(c, (sp.Expr, sp.Basic)):  # Ensure c is a sympy object
        simplified_constraints.append(c.subs(substitutions))
    else:
        print(f"Unexpected non-sympy object: {c} of type {type(c)}")

# Generate a simplified list of constraints.
simplified_strings = [sp.sstr(c) for c in simplified_constraints]

# Convert double-underscores back to periods
final_constraints = [s.replace('__', '.').replace("Contains", "in") for s in simplified_strings]

# Remove duplicate constraints
final_constraints = list(set(final_constraints))

# Determine which symbols from the original list are present in the final constraints
final_sympy_symbols_set = set()
for c in simplified_constraints:
    final_sympy_symbols_set.update(c.atoms(sp.Symbol))

final_symbols = []
final_symbol_types = []

for i, orig_sym in enumerate(symbols):
    mod_sym = orig_sym.replace('.', '__')
    if sympy_symbols[mod_sym] in final_sympy_symbols_set:
        final_symbols.append(orig_sym)
        final_symbol_types.append(symbol_types[i])

#print(final_symbols)
#print(final_symbol_types)

#print(len(final_constraints))

#print(final_constraints)

import os
import re
from pyomo.environ import *

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
        #print(constr_expr,f'constr_{str(jdx)}')
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
