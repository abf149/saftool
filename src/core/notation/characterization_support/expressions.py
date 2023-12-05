'''Helper functions for parsing expressions that filter and aggregate characterization metrics'''
import core.notation.predicates as p_
import sympy as sp
from core.helper import info,warn,error
import csv, re

def parenthesized_expression_to_regex(name_expression, sym_list):
    """Converts a name_expression with parenthesized variables to a regular expression."""
    for sym in sym_list:
        name_expression = name_expression.replace(f"$({sym})", r"\d+")
    regex_pattern = "^" + name_expression + "$"
    return regex_pattern
def match_expression_with_parentheses(names, name_expression, sym_list):
    """Matches a list of names against a name_expression with parenthesized variables."""
    regex_pattern = parenthesized_expression_to_regex(name_expression, sym_list)
    matching_names_and_idxs = [name_ for name_ in names if re.match(regex_pattern,name_)]
    return matching_names_and_idxs
def extract_variable_values(name_expression, sym_list, results):
    """Extract unique values for each variable in the given expression based on the results."""
    regex_patterns = {}
    for sym in sym_list:
        pattern = name_expression.replace(f"$({sym})", r"(\d+)")
        for other_sym in sym_list:
            if sym != other_sym:
                pattern = pattern.replace(f"$({other_sym})", r"\d+")
        regex_patterns[sym] = re.compile(pattern)
    
    variable_values = {sym: set() for sym in sym_list}
    for result in results:
        for sym, pattern in regex_patterns.items():
            match = pattern.match(result)
            if match:
                value = int(match.group(1))
                variable_values[sym].add(value)
                
    for sym in sym_list:
        variable_values[sym] = [int(val_str) for val_str in list(variable_values[sym])]
        variable_values[sym].sort()
    
    return variable_values
def pack_variable_values(name_expression, sym_list, results):
    """Pack the values of the variables for each entry in results into individual dictionaries."""
    pattern = name_expression
    for sym in sym_list:
        pattern = pattern.replace(f"$({sym})", r"(\d+)")
    regex_pattern = re.compile(pattern)
    
    packed_values_list = []
    for result in results:
        match = regex_pattern.match(result)
        if match:
            packed_values = {sym: int(value) for sym, value in zip(sym_list, match.groups())}
            packed_values_list.append(packed_values)
    
    return packed_values_list

def column_expression_to_column_idx_dict(column_expression, column_name_list):
    # Create a mapping from column name to its index in the list
    return {name: idx for idx, name in enumerate(column_name_list)}

def isNumeric(v):
    try:
        float(v)
        return True
    except:
        return False

def column_expression_to_fxn(column_expression, column_name_list):
    # Create a list of symbols using the column_name_list
    symbol_to_index = column_expression_to_column_idx_dict(column_expression, column_name_list)
    symbols = sp.symbols(column_name_list)

    # Parse the column_expression using these symbols
    expr = sp.sympify(column_expression, dict(zip(column_name_list, symbols)))
    
    # Identify which symbols are actually present in the column_expression
    if isinstance(expr,bool):
        used_symbols = []
    elif isinstance(expr, sp.Symbol):
        used_symbols = [expr]
    else:
        used_symbols = [symbol for symbol in symbols if symbol in expr.free_symbols]

    # Create a lambda function to evaluate the expression using values from a given CSV row
    if not isinstance(expr,bool):
        lmbd = lambda row: expr.subs(
                {symbols[symbol_to_index[str(symbol)]]: \
                    row[symbol_to_index[str(symbol)]] \
                        for symbol in used_symbols if isNumeric(row[symbol_to_index[str(symbol)]])}
            )
    else:
        lmbd = lambda row: expr
    
    return lmbd

def column_expression_to_float_fxn(column_expression, column_name_list):
    lmbd_base=column_expression_to_fxn(column_expression, column_name_list)
    return lambda row: float(lmbd_base(row))

def column_expression_to_bool_fxn(column_expression, column_name_list):
    lmbd_base=column_expression_to_fxn(column_expression, column_name_list)
    return lambda row: bool(lmbd_base(row))

def single_var_range_expression_to_lambda(range_expression,sym_name):
    # Create a symbol for clock
    clock = sp.symbols(sym_name)
    
    # Parse the range_expression using this symbol
    expr = sp.sympify(range_expression, {sym_name: clock})
    
    # Create a lambda function to evaluate the expression using a given value of clock and return boolean
    constraint_lambda=lambda clock_value: expr
    if not isinstance(expr,bool):
        constraint_lambda = lambda clock_value: bool(expr.subs(clock, clock_value))

    return constraint_lambda