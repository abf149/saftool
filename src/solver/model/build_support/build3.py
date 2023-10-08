from util.helper import info, warn, error
import util.model.CasCompat as cc_
import sympy as sp
import solver.model.build_support.abstraction as ab_

def build3_simplify_system(problem_as_system):
    warn("- Build phase 3: simplify.")
    info("-- Simplifying...")

    symbols=problem_as_system["symbols"]
    symbol_types=problem_as_system["symbol_types"]
    constraints=problem_as_system["constraints"]
    yields=problem_as_system["yields"]
    flat_yields=[yields[comp_name][attr_][0] \
                    for comp_name in yields \
                        for attr_ in yields[comp_name] \
                            if yields[comp_name][attr_][1]=='sym']

    # Replace periods with double-underscores
    modified_symbols = [cc_.create_safe_symbol(s) for s in symbols]
    modified_constraints = [cc_.create_safe_constraint(c) for c in constraints]

    # Convert modified symbols into sympy symbols
    sympy_symbols = {s: sp.Symbol(s) for s in modified_symbols}

    def convert_to_sympy_expr(constraint, symbols_dict):
        # Handle Piecewise expressions without splitting
        if 'Piecewise' in constraint:
            return sp.sympify(constraint, locals=symbols_dict)
        
        if '==' in constraint:
            lhs, rhs = constraint.split('==')
            return sp.Eq(sp.sympify(lhs.strip(), locals=symbols_dict), sp.sympify(rhs.strip(), locals=symbols_dict))
        
        #print(constraint)
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
    final_constraints = [cc_.adjust_set_membership_syntax(cc_.recover_unsafe_symbol(s)) \
                            for s in simplified_strings]

    simplified_strings_no_bool=[simplified_strings[idx] \
                                        for idx,c in enumerate(final_constraints)  \
                                            if c != "True" and c != "False"]
    final_constraints = [c for c in final_constraints if c != "True" and c != "False"]

    assert(len(simplified_strings_no_bool)==len(final_constraints))

    # Remove duplicate constraints
    
    simplified_strings_no_bools_no_repeats=[]
    new_final_constraints=[]
    for c,safe_c in zip(final_constraints,simplified_strings_no_bool):
        if c not in new_final_constraints:
            simplified_strings_no_bools_no_repeats.append(safe_c)
            new_final_constraints.append(c)
    
    final_constraints=new_final_constraints
    #final_constraints = list(set(final_constraints))

    # First-pass: compute a mapping from symbols to lists of indices of constraints containing those symbols
    # (considering all of the simplified constraints)
    constraint_syms=[]
    constraint_non_yield_syms=[]
    sym_to_const_idxs={}
    new_simplified_constraints=[]
    for idx,_ in enumerate(final_constraints):
        #if "in" not in c_unsafe and (not("And(" in c_unsafe or "Or(" in c_unsafe)):
        c_safe=simplified_strings_no_bools_no_repeats[idx]
        #c_safe=revert_set_membership_syntax(create_safe_constraint(c_unsafe))
        s_exp=convert_to_sympy_expr(c_safe, sympy_symbols) 
        new_simplified_constraints.append(s_exp)
        syms=s_exp.atoms(sp.Symbol)
        
        sym_name_list=[]
        non_yield_sym_name_list=[]
        non_yield_sym_count=0
        for sym in syms:
            sym_name=str(sym)
            sym_name_list.append(sym_name)
            if cc_.create_safe_symbol(sym_name) not in flat_yields:
                non_yield_sym_name_list.append(sym_name)
                non_yield_sym_count+=1
                if sym_name not in sym_to_const_idxs:
                    sym_to_const_idxs[sym_name]=[idx]
                else:
                    sym_to_const_idxs[sym_name].append(idx)

        constraint_syms.append(sym_name_list)
        constraint_non_yield_syms.append(non_yield_sym_name_list)

    # Second-pass: remove a constraint if it is the only constraint which utilizes a particular non-yield symbol
    discarded_constraints=[]
    for non_yield_sym_name in sym_to_const_idxs:
        const_idx_list=sym_to_const_idxs[non_yield_sym_name]
        if len(const_idx_list)==1:
            const_idx=const_idx_list[0]
            const=final_constraints[const_idx]
            if const is not None:
                discarded_constraints.append(final_constraints[const_idx])
                final_constraints[const_idx]=None

    # Third-pass: 
    lb_dict={}
    for non_yield_sym_name in sym_to_const_idxs:

        const_idx_list=sym_to_const_idxs[non_yield_sym_name]
        if len(const_idx_list)>=1:
            add_lb_const=False
            lb_val=-1
            lb_idxs=[]

            yield_sym_ub_set=set()
            yield_sym_lb_set=set()
            non_yield_sym_ub_set=set()
            non_yield_sym_lb_set=set()

            if all([(new_simplified_constraints[idx] is None) or \
                    (new_simplified_constraints[idx].is_Relational and \
                    ("/" not in str(new_simplified_constraints[idx])) and \
                        (("-" not in str(new_simplified_constraints[idx])) \
                         or \
                         ("e-" == str(new_simplified_constraints[idx])[(str(new_simplified_constraints[idx]).index("-")-1):][0:2])))
                            for idx in const_idx_list]):

                for idx in const_idx_list:
                    const_=new_simplified_constraints[idx]
                    if const_ is not None:
                        # Skip constraints which are None
                        #syms=new_simplified_constraints[idx].atoms(sp.Symbol)
                        lhs_=const_.lhs
                        rhs_=const_.rhs
                        lhs_syms=lhs_.atoms(sp.Symbol)
                        rhs_syms=rhs_.atoms(sp.Symbol)
                        oper=""
                        if "<=" in str(const_):
                            oper="<="
                        elif "<" in str(const_):
                            oper="<"
                        elif ">=" in str(const_):
                            oper=">="
                        elif ">" in str(const_):
                            oper=">"
                        else:
                            assert(False)

                        for s in rhs_syms:
                            s_unsafe_str=cc_.recover_unsafe_symbol(str(s))
                            if oper=="<=" or oper=="<":
                                if s_unsafe_str in flat_yields:
                                    yield_sym_ub_set.add(s)
                                else:
                                    if len(lhs_syms)==0:
                                        # <float> < x or <float> <= x
                                        add_lb_const=True
                                        lb_val=max(lb_val,float(lhs_))
                                        lb_idxs.append(idx)
                                    else:
                                        non_yield_sym_ub_set.add(s)
                            else: #">=" or ">"
                                if s_unsafe_str in flat_yields:
                                    yield_sym_lb_set.add(s)
                                else:
                                    non_yield_sym_lb_set.add(s)                            

                        for s in lhs_syms:
                            s_unsafe_str=cc_.recover_unsafe_symbol(str(s))
                            if oper=="<=" or oper=="<":
                                if s_unsafe_str in flat_yields:
                                    yield_sym_lb_set.add(s)
                                else:
                                    non_yield_sym_lb_set.add(s)
                            else: #">=" or ">"
                                if s_unsafe_str in flat_yields:
                                    yield_sym_ub_set.add(s)
                                else:
                                    if len(rhs_syms)==0:
                                        # x > <float> or x >= <float>
                                        add_lb_const=True
                                        lb_val=max(lb_val,float(rhs_))
                                        lb_idxs.append(idx)
                                    else:
                                        non_yield_sym_ub_set.add(s)                          

            n_y_lb=len(non_yield_sym_lb_set)
            n_y_ub=len(non_yield_sym_ub_set)
            y_lb=len(yield_sym_lb_set)
            y_ub=len(yield_sym_ub_set)
        
            if (n_y_lb==1 and n_y_ub==0 and y_lb==0) or \
                    (n_y_lb==0 and n_y_ub==1 and y_ub==0):
                # Eliminate all constraints associated with a non-yield symbol if
                # - The non-yield symbol is not part of a non-relation expression
                # - AND The non-yield symbol is not part of an expression with division or negation
                # - AND It is the only non-yield symbol in all of the relations it is part of
                # - AND one of the following is true: non-yield symbol is ALWAYS just one of gt, gte, lt, or lte
                # - AND if non-yield symbol is {gt or gte,lt or lte} then yield symbol(s) are {lt or lte,gt or gte}
                #
                # In which case, delete all relations associated with the non-yield symbol
                if add_lb_const:
                    # But! there happens to be a lower-bound expression for the non-yield symbol
                    # under consideration.
                    for idx in lb_idxs:
                        # Discard <float> < x or <float> <= x or x > <float> or x >= <float>
                        discarded_constraints.append(final_constraints[idx])
                        final_constraints[idx]=None
                        new_simplified_constraints[idx]=None

                    # Save the lower-bound value to be substituted later
                    lb_dict[non_yield_sym_name]=lb_val
                else:
                    # Non lower-bound expression
                    for idx in const_idx_list:
                        discarded_constraints.append(final_constraints[idx])
                        final_constraints[idx]=None
                        new_simplified_constraints[idx]=None

    # Substitute any lower-bounds discovered above
    for idx,c_sympy in enumerate(new_simplified_constraints):
        c=final_constraints[idx]
        if (c_sympy is not None) and (c is not None) and c_sympy.is_Relational:
            new_c_sympy=c_sympy.subs(lb_dict)
            new_c=cc_.adjust_set_membership_syntax(cc_.recover_unsafe_symbol(str(new_c_sympy)))
            new_simplified_constraints[idx]=new_c_sympy
            final_constraints[idx]=new_c

    # Finally
    new_simplified_constraints=[new_simplified_constraints[idx] \
                                    for idx,c in enumerate(final_constraints) \
                                        if (c is not None) and (c != 'True')]
    final_constraints=[c for c in final_constraints if (c is not None) and (c != 'True')]

    assert(len([c for c in final_constraints if c == 'False'])==0)
    assert(len(new_simplified_constraints)==len(final_constraints))

    #assert(False)

    # Determine which symbols from the original list are present in the final constraints
    final_sympy_symbols_set = set()
    for c in new_simplified_constraints:
        final_sympy_symbols_set.update({str(sym) for sym in c.atoms(sp.Symbol)})

    for y in flat_yields:
        final_sympy_symbols_set.update({cc_.create_safe_symbol(y),})

    final_symbols = []
    final_symbol_types = []

    for i, orig_sym in enumerate(symbols):
        mod_sym = cc_.create_safe_symbol(orig_sym)
        if mod_sym in final_sympy_symbols_set:
            final_symbols.append(orig_sym)
            final_symbol_types.append(symbol_types[i])

    for new_sym in final_sympy_symbols_set:
        new_sym_unsafe=cc_.recover_unsafe_symbol(str(new_sym))
        if new_sym_unsafe not in final_symbols:
            final_symbols.append(new_sym_unsafe)
            if new_sym not in flat_yields:
                final_symbol_types.append('float')
            else:
                final_symbol_types.append('int')

    final_symbols_and_types=list(set([(sym,typ) for sym,typ in zip(final_symbols,final_symbol_types)]))
    final_symbols=[sym_typ[0] for sym_typ in final_symbols_and_types]
    final_symbol_types=[sym_typ[1] for sym_typ in final_symbols_and_types]

    assert(len(final_symbols)==len(list(set(final_symbols))))
    assert(len(final_symbols)==len(final_symbol_types))
    #assert(False)


    simplified_problem={key_:problem_as_system[key_] for key_ in problem_as_system}
    simplified_problem["simplified_symbols"]=final_symbols
    simplified_problem["simplified_symbol_types"]=final_symbol_types
    simplified_problem["simplified_constraints"]=final_constraints

    assert(len(final_symbols)==len(final_symbol_types))

    assert(len([s for s in final_symbols if ("_thresh" not in s) or (s not in flat_yields)])==0)

    warn("-- => done simplifying.")
    warn("-- SIMPLIFY RESULTS:")
    info("  input:",len(symbols),"symbols,",len(constraints),"constraints")
    info("  output:",len(final_symbols),"symbols,",len(final_constraints),"constraints")
    info("  Yield symbols & types (",len(final_symbols),")")
    for comp in yields:
        y_lst=[ab_.uri(comp,sym) for sym in yields[comp] if yields[comp][sym][1]=='sym']
        y_sym_info=[(s,t,str(s in flat_yields)) \
            for s,t in zip(final_symbols,final_symbol_types) if s in y_lst]
        info("  =>",comp,"(",len(y_sym_info),")")
        info('\n', \
            '  ------------------\n', \
            '  ',''.join('%s: type=%s, yield=%s\n' % tpl for tpl in y_sym_info), \
            '  ------------------\n')


    n_y_sym_info=[(s,t,str(s in flat_yields)) \
        for s,t in zip(final_symbols,final_symbol_types) if s not in flat_yields]
    info("  Non-yield symbols & types (",len(n_y_sym_info),")")
    info('\n', \
        '  ------------------\n', \
        '  ',''.join('%s: type=%s, yield=%s\n' % tpl for tpl in n_y_sym_info), \
        '  ------------------\n')

    info("  Final constraints (",len(final_constraints),")")
    info('\n', \
        '  ------------------\n', \
        '  ',''.join('%s\n' % cnst for cnst in final_constraints), \
        '  ------------------\n')

    non_none_discards=[cnst for cnst in discarded_constraints if cnst is not None]
    info("  Discarded constraints (",len(non_none_discards),")")
    info('\n', \
        '  ------------------\n', \
        '  ',''.join('%s\n' % cnst for cnst in non_none_discards), \
        '  ------------------\n')

    warn("- => done, build phase 3.")

    return simplified_problem