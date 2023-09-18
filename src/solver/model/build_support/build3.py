from util.helper import info, warn, error
import sympy as sp

def build3_simplify_system(problem_as_system):
    info("- build phase 3: simplify.")

    symbols=problem_as_system["symbols"]
    symbol_types=problem_as_system["symbol_types"]
    constraints=problem_as_system["constraints"]

    warn("-- input:",len(symbols),"symbols,",len(constraints),"constraints")

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

    simplified_problem={key_:problem_as_system[key_] for key_ in problem_as_system}
    simplified_problem["simplified_symbols"]=final_symbols
    simplified_problem["simplified_symbol_types"]=final_symbol_types
    simplified_problem["simplified_constraints"]=final_constraints

    assert(len(final_symbols)==len(final_symbol_types))

    warn("-- output:",len(final_symbols),"symbols,",len(final_constraints),"constraints")

    info("- => Done, build phase 3.")

    return simplified_problem