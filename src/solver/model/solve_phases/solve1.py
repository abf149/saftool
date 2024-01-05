'''Solve a simplified scale inference problem'''
import os
import re
from pyomo.environ import ConcreteModel, Var, Integers, NonNegativeReals, Constraint,  \
                          Binary, Objective, minimize, SolverManagerFactory, SolverStatus, TerminationCondition
from core.helper import info,warn,error
import core.model.CasCompat as cc_
import sympy as sp

supported_neos_solver_opts=['couenne', 'cbc', 'cplex', 'filmint', 'mosek', 'octeract']

'''
def evaluate_expression(final_objective, model, variable_mapping):

    Parse sympy-compatible objective function expression string (final_objective)
    and generate a pyomo-compatible objective function expression


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
'''

def evaluate_expression(final_objective, model, variable_mapping):
    '''
    Parse sympy-compatible objective function expression string (final_objective)
    and generate a pyomo-compatible objective function expression
    '''

    # Tokenize with improved regex to handle scientific notation
    tokens = re.findall(r"[\w.]+[eE][-+]?[\d]+|[+-/*()]|[\w.]+", final_objective)

    # Parse
    stack = []
    operators = ['+', '-', '*', '/', '(', ')']
    symbol_dict = {}
    for token in tokens:
        if token in operators:
            stack.append(token)
        elif cc_.recover_unsafe_symbol(token) in variable_mapping:
            unsafe_token_name = cc_.recover_unsafe_symbol(token)
            symbol_dict[unsafe_token_name] = getattr(model, variable_mapping[cc_.recover_unsafe_symbol(token)])
            stack.append(f"symbol_dict['{unsafe_token_name}']")
        else:
            try:
                stack.append(float(token))
            except ValueError:
                raise ValueError(f"Unknown token: {token}")

    # Generate
    pymathprog_expr = ''.join(map(str, stack))
    result = eval(pymathprog_expr)
    return result
    
def solve1_scale_inference_simplified_problem(final_symbols,final_symbol_types,final_constraints,final_objective,yields, \
                                              solver_man="neos",solver_opt="filmint",args={'neos_email':'abf149@mit.edu'}):

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
        #print(constraint)
        if 'in(' not in constraint and '|' not in constraint and '&' not in constraint:
            # Transform the constraint with the new variable names
            for original in sorted_symbols:
                mapped = variable_mapping[original]
                constraint = constraint.replace(original, f"model.{mapped}")
            #print("-",constraint)
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
                    setattr(model, f'constr_{jdx}_{variable_mapping[var]}_{v}_upper', Constraint(expr=getattr(model, variable_mapping[var]) - v <= max_val * (1 - bin_var)))
                    setattr(model, f'constr_{jdx}_{variable_mapping[var]}_{v}_lower', Constraint(expr=getattr(model, variable_mapping[var]) - v >= -max_val * (1 - bin_var)))
                    idx+=1
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
                        model.add_component(f'link_{jdx}_and_{idx}_{j}_upper', Constraint(expr=getattr(model, variable_mapping[var]) - var_val <= M * (1 - binary_and_vars[j])))
                        model.add_component(f'link_{jdx}_and_{idx}_{j}_lower', Constraint(expr=getattr(model, variable_mapping[var]) - var_val >= -M * (1 - binary_and_vars[j])))

                # Check if all conditions of the AND are true
                model.add_component(f'constr_{jdx}_and_{idx}', Constraint(expr=sum(binary_and_vars) - len(and_parts) * binary_or_vars[idx] == 0))

            model.add_component(f'constr_or_{jdx}', Constraint(expr=sum(binary_or_vars) >= 1))

    # Objective function
    obj_expr=evaluate_expression(final_objective, model, variable_mapping)
    #obj_expr=sum(getattr(model, variable_mapping[sym]) for sym in final_symbols)
    model.obj = Objective(expr=obj_expr, sense=minimize)

    '''
    for constraint in model.component_objects(Constraint, active=True):
        constraint_object = getattr(model, constraint.name)
        for index in constraint_object:
            print(f"Constraint {constraint.name}[{index}]: {constraint_object[index].expr}")
    '''

    # Assuming variable_mapping is your existing dictionary from real names to encoded names
    # Create a reverse mapping from encoded names to real names

    # Assuming variable_mapping is your existing dictionary from real names to encoded names
    # Create a reverse mapping from encoded names to real names
    reverse_mapping = {v: k for k, v in variable_mapping.items()}

    for constraint in model.component_objects(Constraint, active=True):
        constraint_object = getattr(model, constraint.name)
        for index in constraint_object:
            # Get the string representation of the constraint expression
            expr_str = str(constraint_object[index].expr)

            # Replace encoded variable names with real names using regular expressions
            for encoded_name, real_name in reverse_mapping.items():
                expr_str = re.sub(r'\b' + re.escape(encoded_name) + r'\b', real_name, expr_str)

            print(f"Constraint {constraint.name}[{index}]: {expr_str}")



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
    best_objective=-1.0
    if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
        best_objective=model.obj()
        info("  Raw solver solution output:")
        info("    Objective:",str(obj_expr))
        info(f"    Objective value: {best_objective}",also_stdout=True)
        warn("  Solution:")

        solution_dict={original:getattr(model, mapped)() for original, mapped in variable_mapping.items()}
        for original in solution_dict:
            info(f"    {original} = {solution_dict[original]}")
    else:
        error("  No solution found!",also_stdout=True)
        info("Terminating.",also_stdout=True)
        assert(False)

    return solution_dict,best_objective

def solve1_populate_analytical_primitive_model_attributes(minlp_solution_dict,scale_problem):
    info("-- Populating analytical primitive model attributes...")
    abstract_analytical_models_dict={}
    primitive_models=scale_problem['primitive_models']
    for primitive_name in primitive_models:
        abstract_analytical_models_dict[primitive_name]={}
        yields=primitive_models[primitive_name].get_yields()
        primitive_models[primitive_name].set_analytical_modeling_attributes(minlp_solution_dict)
        abstract_analytical_models_dict[primitive_name]["attributes"]= \
            primitive_models[primitive_name].get_analytical_modeling_attributes(force_inherit=True)
        abstract_analytical_models_dict[primitive_name]["category"]= \
            primitive_models[primitive_name].get_category()

        attr_names, attr_vals = primitive_models[primitive_name].get_yield_attributes_names_and_vec()

        abstract_analytical_models_dict[primitive_name]["attribute_names"]=attr_names
        abstract_analytical_models_dict[primitive_name]["attribute_values"]=attr_vals
    warn("-- => done populating analytical primitive model attributes.")
    warn("-- SUMMARY OF ABSTRACT ANALYTICAL PRIMITIVE MODEL SOLUTION:")
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

def solve1_populate_analytical_component_model_attributes(minlp_solution_dict,scale_problem,component_energy_action_tree):

    info("-- Populating analytical component model attributes...")
    abstract_analytical_models_dict={}
    component_models=scale_problem['component_models']
    for component_name in component_models:
        abstract_analytical_models_dict[component_name]={}
        yields=component_models[component_name].get_yields()
        component_models[component_name].set_analytical_modeling_attributes(minlp_solution_dict)
        abstract_analytical_models_dict[component_name]["category"]= \
            component_models[component_name].get_category()
        abstract_analytical_models_dict[component_name]["attributes"]= \
            component_models[component_name].get_analytical_modeling_attributes(force_inherit=True)
        abstract_analytical_models_dict[component_name]["subcomponent_list"]= \
            component_models[component_name].get_subcomponent_list()
        attr_names, attr_vals = component_models[component_name].get_yield_attributes_names_and_vec()

        abstract_analytical_models_dict[component_name]["attribute_names"]=attr_names
        abstract_analytical_models_dict[component_name]["attribute_values"]=attr_vals
        abstract_analytical_models_dict[component_name]["component_energy_action_tree"]= \
            component_energy_action_tree[component_name]
#        abstract_analytical_models_dict[primitive_name]["attribute_types"]= \
#            [for y in yields]
    warn("-- => done populating analytical model attributes.")
    warn("-- SUMMARY OF ABSTRACT ANALYTICAL COMPONENT MODEL SOLUTION:")
    info("  Model attribute breakdown (",len(list(abstract_analytical_models_dict.keys())),"analytical models):")
    for component_name in abstract_analytical_models_dict:
        comp_model_params=abstract_analytical_models_dict[component_name]
        category=comp_model_params["category"]
        attrs_dict=comp_model_params["attributes"]
        actions_dict=comp_model_params["component_energy_action_tree"]
        info("   ",component_name,":")
        info("    (",category,")")
        info("    - Attributes","(",len(list(attrs_dict.keys())),"):")
        for attr_ in attrs_dict:
            info("        -",attr_,"=",attrs_dict[attr_])
        info("    - Actions","(",len(list(actions_dict.keys())),"):")
        for action in actions_dict:
            subcomponent_action_dict=actions_dict[action]
            info("        -",action)
            for subcomponent in subcomponent_action_dict:
                subaction_dict=subcomponent_action_dict[subcomponent]
                info("            -",subcomponent)
                for subaction in subaction_dict:
                    info("                -",subaction)                    
                    #params=subaction_dict[subaction]
                    # TODO: support arg_map
                    #arg_map=params['arg_map']
                    #if len(list(arg_map.keys))>0:
                    #    info("                -")
                    #else:


    return abstract_analytical_models_dict

def solve1_scale_inference(scale_problem):
    warn("- Solve phase 1: solve MINLP")
    simplified_symbols=scale_problem["simplified_symbols"]
    simplified_symbol_types=scale_problem["simplified_symbol_types"]
    simplified_constraints=scale_problem["simplified_constraints"]
    simplified_objective_function=scale_problem["global_objective"]
    buffer_action_tree=scale_problem["buffer_action_tree"]
    #sub_action_graph=scale_problem["sub_action_graph"]
    component_energy_action_tree=scale_problem["component_energy_action_tree"]
    yields=scale_problem["yields"]
    user_attributes=scale_problem["user_attributes"]
    solver_attributes=user_attributes["scale_inference_solver"]

    minlp_solution_dict, \
    best_objective=solve1_scale_inference_simplified_problem(simplified_symbols,simplified_symbol_types, \
                                                             simplified_constraints,simplified_objective_function, \
                                                             yields,solver_man=solver_attributes['manager'], \
                                                             solver_opt=solver_attributes['solver'], \
                                                             args=solver_attributes['args'])

    # Duplicate solution_dict within problem struct for later reference
    scale_problem['best_modeling_objective']=best_objective
    scale_problem['minlp_solution_dict']=minlp_solution_dict

    abstract_analytical_primitive_models_dict= \
        solve1_populate_analytical_primitive_model_attributes(minlp_solution_dict,scale_problem)
    
    abstract_analytical_component_models_dict= \
        solve1_populate_analytical_component_model_attributes(minlp_solution_dict,scale_problem, \
                                                              component_energy_action_tree)

    warn("- => done, solve phase 1.")
    return abstract_analytical_primitive_models_dict,abstract_analytical_component_models_dict