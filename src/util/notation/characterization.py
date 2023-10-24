import util.notation.predicates as p_
import sympy as sp
from util.helper import info,warn,error
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
    #print(column_name_list)
    #print(symbol_to_index)
    symbols = sp.symbols(column_name_list)

    # Parse the column_expression using these symbols
    expr = sp.sympify(column_expression, dict(zip(column_name_list, symbols)))
    
    # Identify which symbols are actually present in the column_expression
    if isinstance(expr, sp.Symbol):
        used_symbols = [expr]
    else:
        used_symbols = [symbol for symbol in symbols if symbol in expr.free_symbols]

    #print(column_expression, used_symbols)

    # Create a lambda function to evaluate the expression using values from a given CSV row
    lmbd = lambda row: float(expr.subs(
            {symbols[symbol_to_index[str(symbol)]]: \
                row[symbol_to_index[str(symbol)]] \
                    for symbol in used_symbols if isNumeric(row[symbol_to_index[str(symbol)]])}
        ))
    
    return lmbd

def column_expression_to_float_fxn(column_expression, column_name_list):
    lmbd_base=column_expression_to_fxn(column_expression, column_name_list)
    return lambda row: float(lmbd_base(row))

def column_expression_to_bool_fxn(column_expression, column_name_list):
    lmbd_base=column_expression_to_fxn(column_expression, column_name_list)
    return lambda row: bool(lmbd_base(row))

def single_var_range_expression_to_lambda(range_expression):
    # Create a symbol for clock
    clock = sp.symbols('clock')
    
    # Parse the range_expression using this symbol
    expr = sp.sympify(range_expression, {'clock': clock})
    
    # Create a lambda function to evaluate the expression using a given value of clock and return boolean
    constraint_lambda = lambda clock_value: bool(expr.subs(clock, clock_value))


    return constraint_lambda

class CharacterizationTableView:
    def __init__(self,view_dict,name_expression,sym_list,column_names):
        self.nameExpression(name_expression)
        self.symList(sym_list)
        self.viewDict(view_dict)
        self.columnNames(column_names)
        self.RTLNames(list(self.view_dict.keys()))
        self.numVars(len(self.sym_list))

    def nameExpression(self,name_expression):
        self.name_expression=name_expression
        return self

    def getNameExpression(self):
        return self.name_expression
    
    def symList(self,sym_list):
        self.sym_list=sym_list
        return self

    def getSymList(self):
        return self.sym_list
    
    def viewDict(self,view_dict):
        self.view_dict=view_dict
        return self

    def getViewDict(self):
        return self.view_dict
    
    def columnNames(self,column_names):
        self.column_names=column_names
        return self

    def getColumnNames(self):
        return self.column_names
    
    def RTLNames(self,rtl_names):
        self.rtl_names=rtl_names
        return self

    def getRTLNames(self):
        return self.rtl_names
    
    def numVars(self,num_vars):
        self.num_vars=num_vars
        return self

    def getNumVars(self):
        return self.num_vars

    def hasVars(self):
        return (self.getNumVars()>0)
    
    def hasCombos(self):
        return (self.getNumVars()>1)

    def getSupportedVariableValues(self):
        '''
        Returns:\n
        - If self.hasVars(), dict[var id str]=var val
        - Else (no vars), return None
        '''
        if self.hasVars():
            return extract_variable_values(self.name_expression, self.sym_list, self.rtl_names)
        
        return None

    def getSupportedVariableValueCombos(self):
        '''
        Returns:\n
        - If self.hasCombos(), list: [{<var id str>:<var val>,<var id str>:<var val>,...},...]
        - Else (no vars or 1 var), return None
        '''
        if self.hasCombos():
            return pack_variable_values(self.name_expression, self.sym_list, self.rtl_names)
        else:
            return None
    
    def getRowsListByName(self,name_):
        return self.view_dict[name_]
    
    def getAggregatedRowsDictByNameAndFilter(self,name_=None,row_filter_expression=None,aggregation_expression=None):

        lmbd_filter=None
        lmbd_agg=None

        if row_filter_expression is None:
            # Default to no filter
            lmbd_filter=lambda row: True
        else:
            lmbd_filter=column_expression_to_fxn(row_filter_expression, self.column_names)

        if aggregation_expression is None:
            # Default to passtrhu (no aggregation)
            lmbd_agg=lambda row: row
            # Default to passtrhu (no aggregation)
            #column_wise_lmbd_list=[column_expression_to_fxn(column, self.column_names) for column in self.column_names]
            #lmbd_agg=lambda row: [lmbd(row) for lmbd in column_wise_lmbd_list]
        else:
            lmbd_agg=column_expression_to_fxn(aggregation_expression, self.column_names)

        if name_ is None:
            return {k:[lmbd_agg(row) for row in self.view_dict[k] if lmbd_filter(row)] for k in self.view_dict}
        else:
            rows=self.getRowsListByName(name_)
            return {name_:[lmbd_agg(row) for row in rows if lmbd_filter(row)]}


    def getAggregatedRowsListByNameAndFilter(self,name_,row_filter_expression,aggregation_expression):
        rows_dict=self.getAggregatedRowsDictByNameAndFilter(name_,row_filter_expression,aggregation_expression)
        return [row for k in rows_dict for row in rows_dict[k]]

class CharacterizationTableLoader:
    def __init__(self,characterization_filepath):
        self.char_filepath=characterization_filepath
        self.char_table={}
        self.columns=None
        self.unique_names=None

    def loadCharacterizationTable(self):
        with open(self.char_filepath, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)        
            for idx,row in enumerate(csv_reader):
                if idx==0:
                    self.columns=row
                else:
                    name_=row[0]
                    self.char_table.setdefault(name_,[]).append(row)
        self.unique_names=list(self.char_table.keys())
        return self
    
    def getColumnIndexFromId(self,column_id):
        return self.columns.index(column_id)
    
    def getColumnIdFromIndex(self,column_idx):
        return self.columns[column_idx]
    
    def getViewMatchingNameExpression(self,name_expression,sym_list,clock_range_expression=None,clock_column_expression=None):
        name_regex=parenthesized_expression_to_regex(name_expression,sym_list)
        name_matches=match_expression_with_parentheses \
                        (self.unique_names, name_expression, sym_list)
        
        ctv_by_name_expression={k:self.char_table[k] for k in name_matches}

        if clock_column_expression is not None:
            if clock_range_expression is None:
                error("Error in getViewMatchingNameExpression: clock_range cannot be None if clock_column_expression is not None.")
                info("Terminating.")
                assert(False)

            clock_lmbd=column_expression_to_fxn(clock_column_expression,self.columns)
            range_lmbd=single_var_range_expression_to_lambda(clock_range_expression)
            valid_clock_lmbd=lambda row: range_lmbd(clock_lmbd(row))

            ctv_by_name_expression={k:[row for row in ctv_by_name_expression[k] if valid_clock_lmbd(row)] for k in ctv_by_name_expression}

        char_table_view=CharacterizationTableView(ctv_by_name_expression, \
                                                  name_expression,sym_list,self.columns)

        return char_table_view,name_regex

class CharacterizationFunction:
    def __init__(self,function_id=None, characterization_table_loader=None, name_expression=None):
        self.function_id=function_id
        self.row_id_expression=None
        self.row_id_symbol_mapping=None
        self.row_id_param_mapping=None
        self.latency_column_expression=None
        self.param_dict={}
        self.helper_column_expression_dict={}
        self.characterization_view_expression=None
        self.characterization_table_loader=characterization_table_loader

    '''Function initialization'''
    def functionId(self,function_id):
        self.function_id=function_id
        return self

    def getFunctionId(self):
        return self.function_id

    def characterizationTableLoader(self,characterization_table_loader):
        self.characterization_table_loader=characterization_table_loader
        return self
    
    def getCharacterizationTableLoader(self):
        return self.characterization_table_loader

    def inheritParameters(self,param_dict):
        '''
        Arguments:\n
        - param_dict -- dict[param_name_str] = param_val
        '''
        self.param_dict=param_dict
        return self
    
    def getInheritedParameters(self):
        return self.param_dict



    '''Row constraints by component type & scale'''
    def rowIdExpression(self,row_id_expression,row_id_symbol_mapping,row_id_param_mapping):
        '''
        Arguments:\n
        - row_id_expression -- desired value of 'name' column in CSV characterization table\n
            - Optionally with $-delimited variables, i.e. 'merger$u' => 'merger'+str(value of u)\n
        - row_id_symbol_mapping -- map variables in row_id_expression to symbols; dict[var_name] = symbol_name\n
        - row_id_param_mapping -- map variables in row_id_expression to parameters; dict[var_name] = param_name\n
        - Collectively row_id_symbol_mapping and row_id_param_mapping must account for all variables in row_id_expression
        '''
        self.row_id_expression=row_id_expression
        self.row_id_symbol_mapping=row_id_symbol_mapping
        self.row_id_param_mapping=row_id_param_mapping
        return self
    
    def getRowIdExpression(self):
        '''
        Returns:\n
        - row_id_expression, row_id_symbol_mapping, row_id_param_mapping\n
        - row_id_expression -- str\n
        - row_id_symbol_mapping -- dict[var_name] = symbol_name\n
        - row_id_param_mapping -- dict[var_name] = param_name
        '''
        return self.row_id_expression,self.row_id_symbol_mapping,self.row_id_param_mapping
    
    '''Row constraints by values of particular columns'''
    def latencyColumnExpression(self,latency_column_expression):
        '''
        Arguments:\n
        - latency_column_expression -- str
        '''
        self.latency_column_expression=latency_column_expression
        return self
    
    def defaultLatencyColumnExpression(self):
        '''
        Derive latency from the default expression against the underlying CSV characterization table:\n

        '''
        return self
    
    def getLatencyColumnExpression(self):
        '''
        Returns: str
        '''
        return self.latency_column_expression
    
    '''Characterization value definition'''
    def helperColumnExpression(self,helper_column_expression_id, \
                                              helper_column_expression):
        self.helper_column_expression_dict[helper_column_expression_id] = \
            helper_column_expression
        return self
    
    def getHelperColumnExpression(self,helper_column_expression_id):
        return self.helper_column_expression_dict[helper_column_expression_id]
    
    def getAllHelperColumnExpressions(self):
        return self.helper_column_expression_dict
    
    def characterizationViewColumnExpression(self,characterization_view_expression):
        self.characterization_view_expression=characterization_view_expression
        return self
    
    def getCharacterizationViewColumnExpression(self):
        return self.characterization_view_expression
    
