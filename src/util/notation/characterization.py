import util.notation.predicates as p_
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

class CharacterizationTableView:
    def __init__(self,view_dict,name_expression,sym_list):
        self.name_expression=name_expression
        self.sym_list=sym_list
        self.view_dict=view_dict
        self.rtl_names=list(self.view_dict.keys())
        self.num_vars=len(self.sym_list)
        self.has_vars=(self.num_vars>0)
        self.has_combos=(self.num_vars>1)

    def getSupportedVariableValues(self):
        return extract_variable_values(self.name_expression, self.sym_list, self.rtl_names)

    def getSupportedVariableValueCombos(self):
        return pack_variable_values(self.name_expression, self.sym_list, self.rtl_names)

    def hasVars(self):
        return self.has_vars
    
    def hasCombos(self):
        return self.has_combos

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
                    self.char_table.setdefault(name_,[]).append(row[1:])
        self.unique_names=list(self.char_table.keys())
        return self
    
    def getColumnIndexFromId(self,column_id):
        return self.columns.index(column_id)
    
    def getColumnIdFromIndex(self,column_idx):
        return self.columns[column_idx]
    
    def getViewMatchingNameExpression(self,name_expression,sym_list):
        name_regex=parenthesized_expression_to_regex(name_expression,sym_list)
        name_matches=match_expression_with_parentheses \
                        (self.unique_names, name_expression, sym_list)
        char_table_view=CharacterizationTableView({k:self.char_table[k] for k in name_matches}, \
                                                   name_expression,sym_list)
        return char_table_view,name_regex

class CharacterizationFunction:
    def __init__(self,view_id=None):
        self.view_id=view_id
        self.row_id_expression=None
        self.row_id_symbol_mapping=None
        self.row_id_param_mapping=None
        self.latency_column_expression=None
        self.param_dict={}
        self.helper_column_expression_dict={}
        self.characterization_view_expression=None

    '''View ID initialization'''
    def viewId(self,view_id):
        self.view_id=view_id
        return self

    def getViewId(self):
        return self.view_id

    def inheritParameters(self,param_dict):
        '''
        Arguments:\n
        - param_dict -- dict[param_name_str] = param_val
        '''
        self.param_dict=param_dict
        return self
    
    def getInheritedParameters(self):
        return self.param_dict

    def resourcePaths(self,resource_paths):
        '''
        Arguments:\n
        - resource_paths -- dict[resource_type_str] = path_str\n
            - Valid resource type strs include "rtl", "hcl", "sim", "char"\n
            - Corresponding to RTL, HCL (i.e. Chisel), simulation (i.e. VCD), and characterization CSV\n
            - Only characterization CSV path must point to a specific file\n
            - RTL/HCL/simulation point to directories
        '''
        self.resource_paths=resource_paths
        return self
    
    def getResourcePaths(self):
        return self.resource_paths

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
    
