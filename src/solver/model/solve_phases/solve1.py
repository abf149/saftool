'''Solve a simplified scale inference problem'''
import os
import re
from pyomo.environ import *
from util.helper import info,warn,error
import util.model.CasCompat as cc_
import sympy as sp

supported_neos_solver_opts=['couenne', 'cbc', 'cplex', 'filmint', 'mosek', 'octeract']

def evaluate_expression(final_objective, model, variable_mapping):
    '''
    Parse sympy-compatible objective function expression string (final_objective)
    and generate a PyMathProg-compatible objective function expression
    '''

    # Tokenize
    safe_final_objective=cc_.create_safe_constraint(final_objective)
    tokens = re.findall(r"[\w.]+|[+-/*()]", safe_final_objective)

    # Parse
    stack = []
    operators = ['+', '-', '*', '/', '(', ')']
    symbol_dict={}
    for token in tokens:
        if token in operators:
            stack.append(token)
        elif cc_.recover_unsafe_symbol(token) in variable_mapping:
            unsafe_token_name=cc_.recover_unsafe_symbol(token)
            symbol_dict[unsafe_token_name]=getattr(model, variable_mapping[cc_.recover_unsafe_symbol(token)])
            stack.append("symbol_dict[\""+unsafe_token_name+"\"]")
        else:
            try:
                stack.append(float(token))
            except ValueError:
                raise ValueError(f"Unknown token: {token}")

    # Generate
    pymathprog_expr=''.join(map(str, stack))
    result = eval(pymathprog_expr)
    return result

def solve1_scale_inference_simplified_problem(final_symbols,final_symbol_types,final_constraints,final_objective,yields, \
                                              solver_man="neos",solver_opt="couenne",args={'neos_email':'abf149@mit.edu'}):

    info("-- Solving MINLP...")
    warn("--- Solver options:","solver_man =",solver_man,"solver_opt =",solver_opt,"args =",args)
    info("--- Converting problem to pyomo syntax...")

    # Create a model instance
    model = ConcreteModel()

    # Mapping symbols to more convenient names
    variable_mapping = {sym: f'x{i+1}' for i, sym in enumerate(final_symbols)}


    # Defining the variables based on their types
    for sym, sym_type in zip(final_symbols, final_symbol_types):
        var_name = variable_mapping[sym]
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
    obj_expr=evaluate_expression(final_objective, model, variable_mapping)
    #obj_expr=sum(getattr(model, variable_mapping[sym]) for sym in final_symbols)
    model.obj = Objective(expr=obj_expr, sense=minimize)

    # Solve the model
    if solver_man=='neos':
        # Tier 1: filmint
        # Tier 2: mosek, couenne, octeract, cbc, cplex

        #['bonmin', 'cbc', 'conopt', 'couenne', 'cplex', 'filmint', 'filter', 
        # 'ipopt', 'knitro', 'l-bfgs-b', 'lancelot', 'lgo', 'loqo', 'minlp', 
        # 'minos', 'minto', 'mosek', 'octeract', 'ooqp', 'path', 'raposa', 'snopt']

        neos_email=args['neos_email']
        info("--- moving forward with NEOS solver, os.environ['NEOS_EMAIL'] =",neos_email)
        os.environ['NEOS_EMAIL'] = neos_email
        solver_manager = SolverManagerFactory(solver_man)
        info("--- supported NEOS solver opts:",''.join("%s " % opt_ for opt_ in supported_neos_solver_opts))
        if solver_opt not in supported_neos_solver_opts:
            # Terminate if invalid solver_opt
            error("--- Invalid NEOS solver_opt",solver_opt,also_stdout=True)
            info("Terminating.",also_stdout=True)
            assert(False)
        warn("--- Starting NEOS job with solver_opt =",solver_opt)
        results = solver_manager.solve(model, opt=solver_opt, tee=True, keepfiles=True) #couenne, cbc, cplex, filmint, mosek, octeract
        if results.solver.status == SolverStatus.ok:
            warn("--- => Solver returned status OK.")
        else:
            error("--- => Solver returned status",str(results.solver.status),"which is not OK.",also_stdout=True)
            info("Terminating.",also_stdout=True)
            assert(False)
    else:
        # Other solver managers not supported
        error("--- Invalid solver manager option",solver_man,also_stdout=True)
        info("Terminating.",also_stdout=True)
        assert(False)

    warn("-- => done solving.")
    warn("-- SOLVE RESULTS:")

    if results.solver.termination_condition == TerminationCondition.optimal:
        warn("  Termination condition: Optimal",also_stdout=True)
    else:
        warn("  Termination condition:",str(results.solver.termination_condition),"which is not Optimal",also_stdout=True)

    # Display results
    solution_dict={}
    if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
        info("  Raw solver solution output:")
        info("    Objective:",str(obj_expr))
        info(f"    Objective value: {model.obj()}",also_stdout=True)
        warn("  Solution:")

        solution_dict={original:getattr(model, mapped)() for original, mapped in variable_mapping.items()}
        for original in solution_dict:
            info(f"    {original} = {solution_dict[original]}")
    else:
        error("  No solution found!",also_stdout=True)
        info("Terminating.",also_stdout=True)
        assert(False)

    return solution_dict

def solve1_populate_analytical_model_attributes(minlp_solution_dict,scale_problem):
    info("-- Populating analytical model attributes...")
    abstract_analytical_models_dict={}
    primitive_models=scale_problem['primitive_models']
    for primitive_name in primitive_models:
        abstract_analytical_models_dict[primitive_name]={}
        yields=primitive_models[primitive_name].get_yields()
        primitive_models[primitive_name].set_analytical_modeling_attributes(minlp_solution_dict)
        abstract_analytical_models_dict[primitive_name]["attributes"]= \
            primitive_models[primitive_name].get_analytical_modeling_attributes()
        abstract_analytical_models_dict[primitive_name]["category"]= \
            primitive_models[primitive_name].get_category()

        attr_names, attr_vals = primitive_models[primitive_name].get_yield_attributes_names_and_vec()

        abstract_analytical_models_dict[primitive_name]["attribute_names"]=attr_names
        abstract_analytical_models_dict[primitive_name]["attribute_values"]=attr_vals
#        abstract_analytical_models_dict[primitive_name]["attribute_types"]= \
#            [for y in yields]
    warn("-- => done populating analytical model attributes.")
    warn("-- SUMMARY OF ABSTRACT ANALYTICAL MODEL SOLUTION:")
    info("  Model attribute breakdown (",len(list(abstract_analytical_models_dict.keys())),"analytical models):")
    for primitive_name in abstract_analytical_models_dict:
        prim_model_params=abstract_analytical_models_dict[primitive_name]
        category=prim_model_params["category"]
        attrs_dict=prim_model_params["attributes"]
        info("   ",primitive_name,"(",len(list(attrs_dict.keys())),"attributes):")
        info("    (",category,")")
        for attr_ in attrs_dict:
            info("    -",attr_,"=",attrs_dict[attr_])

    return abstract_analytical_models_dict

def solve1_scale_inference(scale_problem):
    warn("- Solve phase 1: solve MINLP")
    simplified_symbols=scale_problem["simplified_symbols"]
    simplified_symbol_types=scale_problem["simplified_symbol_types"]
    simplified_constraints=scale_problem["simplified_constraints"]
    simplified_objective_function=scale_problem["global_objective"]
    yields=scale_problem["yields"]
    minlp_solution_dict=solve1_scale_inference_simplified_problem(simplified_symbols,simplified_symbol_types, \
                                                                  simplified_constraints,simplified_objective_function, \
                                                                  yields,solver_man="neos",solver_opt="filmint", \
                                                                  args={'neos_email':'abf149@mit.edu'})

    # Duplicate solution_dict within problem struct for later reference
    scale_problem['minlp_solution_dict']=minlp_solution_dict

    abstract_analytical_models_dict= \
        solve1_populate_analytical_model_attributes(minlp_solution_dict,scale_problem)

    warn("- => done, solve phase 1.")
    return abstract_analytical_models_dict