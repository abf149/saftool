import core.notation.predicates as p_
import core.notation.model as mo_
import sympy as sp
from core.helper import info,warn,error,get_tqdm_outfile
import csv, re
import core.model.CasCompat as cc_
import core.notation.characterization_support.expressions as ex_
import core.notation.characterization_support.fit as fit_
import copy
from tqdm import tqdm

class CharacterizationTableView:
    def __init__(self,view_dict,name_expression,var_list,column_names,latency_lmbd):
        self.latency_lmbd=latency_lmbd
        self.nameExpression(name_expression)
        self.varList(var_list)
        self.viewDict(view_dict)
        self.columnNames(column_names)
        self.RTLNames(list(self.view_dict.keys()))
        self.numVars(len(self.var_list))

    def nameExpression(self,name_expression):
        self.name_expression=name_expression
        return self

    def getNameExpression(self):
        return self.name_expression
    
    def getLatencyLambda(self):
        return self.latency_lmbd

    def varList(self,var_list):
        self.var_list=var_list
        return self

    def getVarList(self):
        return self.var_list
    
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
            return ex_.extract_variable_values(self.name_expression, self.var_list, self.rtl_names)
        
        return None

    def getSupportedVariableValueCombos(self):
        '''
        Returns:\n
        - If self.hasCombos(), list: [{<var id str>:<var val>,<var id str>:<var val>,...},...]
        - Else (no vars or 1 var), return None
        '''
        if self.hasCombos():
            return ex_.pack_variable_values(self.name_expression, self.var_list, self.rtl_names)
        else:
            return None
    
    def getRowsListByName(self,name_):
        return self.view_dict[name_]
    
    def getRowsListByVariablesDict(self,vars_dict):
        name_=self.varsDictToName(vars_dict)
        return self.getRowsListByName(name_)

    def getAggregatedRowsDictByNameAndFilter(self,name_=None,row_filter_expression=None, \
                                             aggregation_expression=None,substitute_in_filter={}):

        if len(substitute_in_filter)>0:
            row_filter_expression_sp=sp.sympify(row_filter_expression)
            sub_dict={sp.sympify(k):sp.sympify(substitute_in_filter[k]) for k in substitute_in_filter}
            row_filter_expression_sp=row_filter_expression_sp.subs(sub_dict)
            row_filter_expression = str(row_filter_expression_sp)

        lmbd_filter=None
        lmbd_agg=None

        if row_filter_expression is None:
            # Default to no filter
            lmbd_filter=lambda row: True
        else:
            lmbd_filter=ex_.column_expression_to_bool_fxn(row_filter_expression, self.column_names)

        if aggregation_expression is None:
            # Default to passtrhu (no aggregation)
            lmbd_agg=lambda row: row
            # Default to passtrhu (no aggregation)
            #column_wise_lmbd_list=[column_expression_to_fxn(column, self.column_names) for column in self.column_names]
            #lmbd_agg=lambda row: [lmbd(row) for lmbd in column_wise_lmbd_list]
        else:
            lmbd_agg=ex_.column_expression_to_fxn(aggregation_expression, self.column_names)

        if name_ is None:
            return {k:[lmbd_agg(row) for row in self.view_dict[k] if lmbd_filter(row)] for k in self.view_dict}
        else:
            rows=self.getRowsListByName(name_)
            return {name_:[lmbd_agg(row) for row in rows if lmbd_filter(row)]}


    def getAggregatedRowsListByNameAndFilter(self,name_,row_filter_expression, \
                                             aggregation_expression,substitute_in_filter={}):
        rows_dict=self.getAggregatedRowsDictByNameAndFilter(name_,row_filter_expression, \
                                                            aggregation_expression,substitute_in_filter)
        return [row for k in rows_dict for row in rows_dict[k]]

    def varsDictToName(self,vars_dict):
        name_=self.getNameExpression()
        for k in vars_dict:
            name_=name_.replace("$("+k+")",str(int(vars_dict[k])))
        return name_

    def getAggregatedRowsListByVariablesDictAndFilter(self,vars_dict,row_filter_expression, \
                                                      aggregation_expression,substitute_in_filter={}):
        name_=self.varsDictToName(vars_dict)
        return self.getAggregatedRowsListByNameAndFilter(name_,row_filter_expression, \
                                                         aggregation_expression,substitute_in_filter)

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
    
    def getViewMatchingNameExpression(self,name_expression,var_list,latency_range_expression=None,latency_column_expression=None):
        name_regex=ex_.parenthesized_expression_to_regex(name_expression,var_list)
        name_matches=ex_.match_expression_with_parentheses \
                        (self.unique_names, name_expression, var_list)
        
        ctv_by_name_expression={k:self.char_table[k] for k in name_matches}

        latency_lmbd=None
        latency_range_lmbd=None
        if latency_column_expression is not None:
            if latency_range_expression is None:
                error("Error in getViewMatchingNameExpression: clock_range cannot be None if clock_column_expression is not None.")
                info("Terminating.")
                assert(False)

            latency_lmbd=ex_.column_expression_to_fxn(latency_column_expression,self.columns)
            latency_range_lmbd=ex_.single_var_range_expression_to_lambda(latency_range_expression,'latency')
            valid_latency_lmbd=lambda row: latency_range_lmbd(latency_lmbd(row))

            ctv_by_name_expression={k:[row for row in ctv_by_name_expression[k] if valid_latency_lmbd(row)] for k in ctv_by_name_expression}

        char_table_view=CharacterizationTableView(ctv_by_name_expression, \
                                                  name_expression,var_list,self.columns, \
                                                  latency_lmbd)

        return char_table_view,name_regex

class CharacterizationMetricModel:
    def __init__(self,function_id=None, characterization_table_loader=None, name_expression=None, var_list=None):
        self.function_id=function_id
        self.parent_uri=None
        self.row_id_expression=None
        self.row_id_symbol_mapping=None
        self.row_id_param_mapping=None
        self.latency_column_expression=None
        self.latency_param_id=None
        self.latency_constant_value=None
        self.param_dict={}
        self.helper_column_expression_dict={}
        self.characterization_view_expression=None
        self.characterization_table_loader=characterization_table_loader
        self.characterization_table_view=None
        #self.user_attributes=None
        self.name_expression=name_expression
        self.var_list=var_list
        self.sym_list=None
        self.sym_map_dict=None
        self.latency_independent_variable_expression=None
        self.latency_range_expression=None
        self.row_energy_metric_expression=None
        self.row_area_metric_expression=None
        self.supported_variable_values=None
        self.supported_variable_value_combos=None
        self.supported_symbol_values_constraints_list=[]
        self.supported_symbol_value_combos_constraints_list=[]
        self.row_energy_lambda=None
        self.row_area_lambda=None
        self.energy_area_latency_independent_vars=None
        self.energy_area_latency_dict=None
        self.energy_area_latency_dataset_column_names=None
        self.energy_area_latency_dataset=None
        self.metric_model_exprs=None
        self.metric_model_lambdas=None
        self.single_latency=None
        self.clock_latency_column=None
        self.supported_symbol_values=None
        self.supported_symbol_value_combos=None

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

    def parentComponentUri(self,parent_uri):
        self.parent_uri=parent_uri
        return self

    def getParentComponentUri(self):
        return self.parent_uri

    '''Create table view'''
    def nameExpression(self,name_expression,var_list):
        self.name_expression=name_expression
        self.var_list=var_list
        return self

    def getNameExpression(self):
        '''
        Return: name_expression
        '''
        return self.name_expression
    
    def getVarList(self):
        return self.var_list

    def symbolMap(self,sym_map_dict):
        self.sym_map_dict=sym_map_dict
        return self

    def getSymbolMap(self):
        return self.sym_map_dict
    
    def latencyIndependentVariableExpression(self,latency_independent_variable_expression):
        self.latency_independent_variable_expression=latency_independent_variable_expression
        return self
    
    def getLatencyIndependentVariableExpression(self):
        return self.latency_independent_variable_expression

    def latencyParameterId(self,latency_param_id,single_latency=False,clock_latency_column=None):
        self.latency_param_id=latency_param_id
        self.single_latency=single_latency
        if single_latency and (clock_latency_column is None):
            # Default clock latency column in characterization table
            clock_latency_column='critical_path_clock_latency'
        self.clock_latency_column=clock_latency_column
        return self
    
    def getLatencyParameterId(self):
        return self.latency_param_id

    def latencyConstantValue(self,latency_constant_value):
        self.latency_constant_value=latency_constant_value
        return self
    
    def getLatencyConstantValue(self):
        return self.latency_constant_value

    def isSingleLatency(self):
        return self.single_latency
    
    def getClockLatencyColumn(self):
        return self.clock_latency_column

    def setSingleLatencyValue(self,val_):
        self.single_latency_value=val_

    def getSingleLatencyValue(self):
        return self.single_latency_value

    def latencyRangeExpression(self,latency_range_expression):
        self.latency_range_expression=latency_range_expression
        return self

    def getLatencyRangeExpression(self):
        return self.latency_range_expression

    #def userAttributes(self,user_attributes):
    #    self.user_attributes=user_attributes
    #    return self
    
    #def getUserAttributes(self):
    #    return self.user_attributes

    def inheritParameters(self,param_dict):
        '''
        Arguments:\n
        - param_dict -- dict[param_name_str] = param_val
        '''
        self.param_dict=param_dict
        return self
    
    def getInheritedParametersDict(self):
        return self.param_dict

    def getInheritedParameterValue(self,param_id):
        return self.getInheritedParametersDict()[param_id]

    '''Metrics'''
    def rowEnergyMetricExpression(self,row_energy_metric_expression):
        self.row_energy_metric_expression=row_energy_metric_expression
        return self
    
    def getRowEnergyMetricExpression(self):
        return self.row_energy_metric_expression

    def rowEnergyMetricFromRowPowerMetricExpression(self,row_power_metric_expression):
        self.row_power_metric_expression=row_power_metric_expression
        return self
    
    def getRowPowerMetricExpression(self):
        return self.row_power_metric_expression

    def rowAreaMetricExpression(self,row_area_metric_expression):
        self.row_area_metric_expression=row_area_metric_expression
        return self
    
    def getRowAreaMetricExpression(self):
        return self.row_area_metric_expression

    '''Build process'''

    def buildSymbolMap(self):
        if self.parent_uri is not None:
            '''
            self.sym_map_dict={var_:self.sym_map_dict[var_].replace("@",self.parent_uri+".") \
                                    for var_ in self.sym_map_dict}
            '''
            self.sym_map_dict={var_:self.sym_map_dict[var_] \
                                    for var_ in self.sym_map_dict}
        return self

    def buildSymList(self):
        var_list=self.getVarList()
        sym_map_dict=self.getSymbolMap()
        self.sym_list=[sym_map_dict[var_] for var_ in var_list]
        return self

    def getSymList(self):
        return self.sym_list

    def buildCharacterizationTableView(self):
        latency_independent_variable_expression=""
        latency_range_expression=""
        if self.getLatencyRangeExpression() is not None:
            latency_independent_variable_expression=self.getLatencyIndependentVariableExpression()
            latency_range_expression=self.getLatencyRangeExpression()
        elif self.latency_param_id is not None:
            # Latency must be in ns
            # TODO: don't required latency in ns
            latency_val=self.getInheritedParameterValue(self.latency_param_id)
            if type(latency_val).__name__=='str':
                if ex_.isNumeric(latency_val):
                    latency_val=float(latency_val)
                elif 'ns' in latency_val:
                    latency_val=float(latency_val.split('ns')[0])
                else:
                    error("clock parameter must be int, float, str which can be cast to float,"+ \
                          " or string of the form \'<number>ns\'",also_stdout=True)
                    info("Terminating.")
                    assert(False)

            if self.isSingleLatency():
                latency_independent_variable_expression=self.getClockLatencyColumn()
                self.setSingleLatencyValue(latency_val)
            else:
                latency_independent_variable_expression=self.getLatencyIndependentVariableExpression()
            latency_range_expression="Eq(latency,"+str(latency_val)+")"

            self.latencyIndependentVariableExpression(latency_independent_variable_expression)
            self.latencyRangeExpression(latency_range_expression)
        elif self.latency_constant_value is not None:
            latency_independent_variable_expression=self.getLatencyIndependentVariableExpression()
            latency_range_expression="Eq(latency,"+str(self.latency_constant_value)+")"
            self.latencyIndependentVariableExpression(latency_independent_variable_expression)
            self.latencyRangeExpression(latency_range_expression)
        else:
            error("CharacterizationMetricModel requires latency to be specified or constrained.",also_stdout=True)
            info("Terminating.")
            assert(False)

        self.characterization_table_view,_ = \
            self.characterization_table_loader.getViewMatchingNameExpression \
                (self.getNameExpression(), \
                 self.getVarList(), \
                 latency_range_expression, \
                 latency_independent_variable_expression)
        return self
        
    def getCharacterizationTableView(self):
        return self.characterization_table_view

    def hasVars(self):
        return self.characterization_table_view.hasVars()

    def hasCombos(self):
        return self.characterization_table_view.hasCombos()

    def buildSupportedConfigurations(self):
        self.supported_variable_values=self.characterization_table_view.getSupportedVariableValues()
        self.supported_variable_value_combos=self.characterization_table_view.getSupportedVariableValueCombos()
        sym_map=self.getSymbolMap()

        if self.hasVars():
            self.supported_symbol_values={sym_map[k]:self.supported_variable_values[k] \
                                            for k in self.supported_variable_values}
        if self.hasCombos():
            self.supported_symbol_value_combos=[ \
                {sym_map[k]:combo_[k] \
                    for k in combo_}
                        for combo_ in self.supported_variable_value_combos
            ]
        return self
    
    def getSupportedVariableValues(self):
        return self.characterization_table_view.getSupportedVariableValues()
    
    def getSupportedVariableValueCombos(self):
        return self.characterization_table_view.getSupportedVariableValueCombos()

    def getSupportedSymbolValues(self):
        if self.hasVars():
            return self.supported_symbol_values
        else:
            return {}
    
    def getSupportedSymbolValueCombos(self):
        if self.hasCombos():
            return self.supported_symbol_value_combos
        else:
            return {}

    def buildSupportedSymbolValuesConstraints(self):
        if self.hasVars():
            supported_symbol_values=self.getSupportedSymbolValues()
            self.supported_symbol_values_constraints_list= \
                [
                    mo_.makeValuesConstraint(sym_, \
                                             foralls=[('a',"attrs",[""])], \
                                             ranges=[tuple(supported_symbol_values[sym_])])
                                                    
                        for sym_ in supported_symbol_values \
                ]
        return self
    
    def buildSupportedSymbolValueCombosConstraints(self):
        if self.hasCombos():
            supported_symbol_value_combos=self.getSupportedSymbolValueCombos()
            sym_list=self.getSymList()
            self.supported_symbol_value_combos_constraints_list= \
                [
                    mo_.makeCombosConstraint(sym_list, \
                                             [tuple([combo_[k] for k in sym_list]) \
                                                for combo_ in supported_symbol_value_combos])
                ]
        return self

    def getRowLatencyLambda(self):
        return self.characterization_table_view.getLatencyLambda()

    def getColumnNames(self):
        return self.characterization_table_view.getColumnNames()

    def buildRowEnergyMetricExpressionIfDerivedFromPower(self):
        row_power_metric_expression=self.getRowPowerMetricExpression()
        latency_independent_variable_expression=self.getLatencyIndependentVariableExpression()
        if self.getRowPowerMetricExpression() is not None:
            # If the user specified a power metric expression, then
            # compute the corresponding energy metric expression
            self.rowEnergyMetricExpression("("+row_power_metric_expression+")*("+ \
                                           latency_independent_variable_expression+")")

        return self

    def buildRowEnergyLambda(self):
        self.row_energy_lambda= \
            ex_.column_expression_to_float_fxn(self.getRowEnergyMetricExpression(), \
                                               self.getColumnNames())
        return self

    def getRowEnergyLambda(self):
        return self.row_energy_lambda
    
    def buildRowAreaLambda(self):
        self.row_area_lambda= \
            ex_.column_expression_to_float_fxn(self.getRowAreaMetricExpression(), \
                                               self.getColumnNames())
        return self

    def getRowAreaLambda(self):
        return self.row_area_lambda

    def buildEnergyAreaLatencyTable(self):
        ctv=self.getCharacterizationTableView()
        latency_independent_variable_expression=self.getLatencyIndependentVariableExpression()
        latency_range_expression=self.getLatencyRangeExpression()
        row_energy_metric_expression=self.getRowEnergyMetricExpression()
        row_area_metric_expression=self.getRowAreaMetricExpression()
        var_list=self.getVarList()
        sym_list=self.getSymList()
        table_independent_variable_points={}
        supported_variable_value_combos=self.getSupportedVariableValueCombos()
        supported_variable_values=self.getSupportedVariableValues()
        
        if supported_variable_value_combos is None:
            assert(supported_variable_values is not None)
            only_var=var_list[0]
            only_var_vals_list=supported_variable_values[only_var]
            supported_variable_value_combos=[{only_var:val_} for val_ in only_var_vals_list]
        elif supported_variable_values is not None:
            pass
        else:
            assert((supported_variable_values is not None) or (supported_variable_value_combos))

        # Progress bar setup
        
        total_iterations = len(supported_variable_value_combos)
        info("--- Building "+self.getNameExpression()+" energy area latency table.")
        pbar = tqdm(total=total_iterations, desc="Building "+self.getNameExpression()+" energy area latency table.", \
                    file=get_tqdm_outfile())

        key_column_names=copy.copy(sym_list)
        key_column_names.append('latency')
        dataset_column_names=key_column_names+['energy','area']

        energy_area_latency_dict={}
        energy_area_latency_dataset=[]
        for combo_ in supported_variable_value_combos:
            key_variables_base=[combo_[var_] for var_ in var_list]

            latency_list= \
                ctv.getAggregatedRowsListByVariablesDictAndFilter(combo_, \
                                                                  latency_range_expression, \
                                                                  latency_independent_variable_expression, \
                                                                  substitute_in_filter= \
                                                                    {"latency": \
                                                                        latency_independent_variable_expression \
                                                                    })
            row_energy_list= \
                ctv.getAggregatedRowsListByVariablesDictAndFilter(combo_, \
                                                                  latency_range_expression, \
                                                                  row_energy_metric_expression, \
                                                                  substitute_in_filter= \
                                                                    {"latency": \
                                                                        latency_independent_variable_expression \
                                                                    })
            row_area_list= \
                ctv.getAggregatedRowsListByVariablesDictAndFilter(combo_, \
                                                                  latency_range_expression, \
                                                                  row_area_metric_expression, \
                                                                  substitute_in_filter= \
                                                                    {"latency": \
                                                                        latency_independent_variable_expression \
                                                                    })

            for idx,latency in enumerate(latency_list):
                energy=row_energy_list[idx]
                area=row_area_list[idx]
                key_=copy.copy(key_variables_base)
                key_.append(latency)
                datapoint=copy.copy(key_)
                datapoint.append(energy)
                datapoint.append(area)
                key_=tuple(key_)
                datapoint=tuple(datapoint)
                if key_ not in energy_area_latency_dict:
                    energy_area_latency_dict[key_]={'energy':energy,'area':area}
                    energy_area_latency_dataset.append(datapoint)

            pbar.update(1)

        pbar.close()
        self.energy_area_latency_independent_vars=key_column_names
        self.energy_area_latency_dict=energy_area_latency_dict
        self.energy_area_latency_dataset_column_names=dataset_column_names
        self.energy_area_latency_dataset=energy_area_latency_dataset
        return self

    def getEnergyAreaLatencyDatasetColumnNames(self):
        return self.energy_area_latency_dataset_column_names

    def getEnergyAreaLatencyDataset(self):
        return self.energy_area_latency_dataset

    def getEnergyAreaLatencyTableIndependentVariableNames(self):
        return self.energy_area_latency_independent_vars

    def getEnergyAreaLatencyDict(self):
        return self.energy_area_latency_dict

    def getSupportedSymbolValuesConstraints(self):
        return self.supported_symbol_values_constraints_list
    
    def getSupportedSymbolValueCombosConstraints(self):
        return self.supported_symbol_value_combos_constraints_list

    def getMetricModelExpressionsDict(self):
        return self.metric_model_exprs

    def getEnergyMetricModelExpression(self):
        return self.getMetricModelExpressionsDict()['energy']

    def getAreaMetricModelExpression(self):
        return self.getMetricModelExpressionsDict()['area']

    def getMetricModelLambdasDict(self):
        return self.metric_model_lambdas

    def getEnergyMetricModelLambda(self):
        return self.getMetricModelLambdasDict()['energy']

    def getAreaMetricModelLambda(self):
        return self.getMetricModelLambdasDict()['area']

    def substituteClockLatencyInExprAndLambda(self,expr,lmbda,independent_var_names,clock_value):
        safe_non_latency_independent_var_names=[cc_.create_safe_symbol(var_name) \
                                                    for var_name in independent_var_names if var_name != 'latency']

        safe_from_prefix_non_latency_independent_var_names=[var_name.replace("@","x___") \
                                                                for var_name in safe_non_latency_independent_var_names]

        latency_sym=sp.symbols('latency')
        #clock_column_name_sym=sp.symbols('clock_column_name')
        clock_column_val_expr=sp.sympify(clock_value)
        expr_safe=cc_.create_safe_constraint(expr)
        expr_safe_from_prefix=expr_safe.replace("@","x___")
        expr_sp=sp.sympify(expr_safe_from_prefix)
        expr_sp_subs=sp.simplify(expr_sp.subs({latency_sym:clock_column_val_expr}))
        expr_subs=str(expr_sp_subs)
        lmbda_subs=sp.lambdify(safe_from_prefix_non_latency_independent_var_names, expr_sp_subs, 'numpy')
        expr_subs_unsafe_from_prefix=expr_subs.replace("x___","@")
        expr_subs_unsafe=cc_.recover_unsafe_symbol(expr_subs_unsafe_from_prefix)
        return expr_subs_unsafe,lmbda_subs

    def buildEnergyAreaMetricModels(self,type_='poly',norm_='StandardScaler'):
        
        name_expression=self.getNameExpression()
        independent_var_names=self.getEnergyAreaLatencyTableIndependentVariableNames()
        column_names=self.getEnergyAreaLatencyDatasetColumnNames()
        dependent_var_names=[var_name for var_name in column_names \
                                if var_name not in independent_var_names]
        data=self.getEnergyAreaLatencyDataset()
        if type_=='poly' and norm_=='StandardScaler':

            fitted_models, \
            scalers, \
            best_degrees, \
            MSEs, \
            NMSEs=fit_.polynomial_regression_generalized_v2(data, \
                                                            column_names, \
                                                            independent_var_names, \
                                                            max_degree=3, \
                                                            overfit=True, \
                                                            show_progress=True)
            
            X_scaler=scalers['X']
            energy_model=fitted_models['energy']
            energy_scaler=scalers['energy']
            energy_best_degree=best_degrees['energy']
            area_model=fitted_models['area']
            area_scaler=scalers['area']
            area_best_degree=best_degrees['area']

            energy_expr, \
            energy_lambda=fit_.polynomial_to_sympy_expression_with_lambda_generalized(energy_model, \
                                                                                      X_scaler, \
                                                                                      energy_scaler, \
                                                                                      energy_best_degree, \
                                                                                      independent_var_names)

            area_expr, \
            area_lambda=fit_.polynomial_to_sympy_expression_with_lambda_generalized(area_model, \
                                                                                    X_scaler, \
                                                                                    area_scaler, \
                                                                                    area_best_degree, \
                                                                                    independent_var_names)
            
            exprs={"energy":energy_expr,"area":area_expr}
            lambdas={"energy":energy_lambda,"area":area_lambda}

            self.metric_model_exprs=exprs
            self.metric_model_lambdas=lambdas

            mse_comparison=fit_.compare_lambda_with_baseline(fitted_models, \
                                                             lambdas, \
                                                             data, \
                                                             column_names, \
                                                             independent_var_names, \
                                                             scalers, \
                                                             best_degrees)

            if mse_comparison['energy'] > 1e-10 or mse_comparison['area'] > 1e-10:
                warn('Warning: mse_comparison[\'energy\'] ==', \
                     mse_comparison['energy'], \
                     'mse_comparison[\'area\'] ==', \
                     mse_comparison['area'], \
                     also_stdout=True)

            info(name_expression,"energy expression:\n",energy_expr)
            info("-",name_expression,"MSE energy error (symbolic vs numerical):",mse_comparison['energy'],also_stdout=True)
            info(name_expression,"area expression:\n",area_expr)
            info("-",name_expression,"MSE area error (symbolic vs numerical):",mse_comparison['area'],also_stdout=True)
    
            if self.isSingleLatency():
                info("- Substituting in clock latency for latency independent variable...")
                # Substitute in clock latency column for latneyc
                clock_column_name=self.getClockLatencyColumn()
                clock_value=self.getSingleLatencyValue()
                energy_expr,energy_lambda=self.substituteClockLatencyInExprAndLambda(energy_expr, \
                                                                                     energy_lambda, \
                                                                                     independent_var_names, \
                                                                                     clock_value)
                area_expr,area_lambda=self.substituteClockLatencyInExprAndLambda(area_expr, \
                                                                                 area_lambda, \
                                                                                 independent_var_names, \
                                                                                 clock_value)
                
                exprs={"energy":energy_expr,"area":area_expr}
                lambdas={"energy":energy_lambda,"area":area_lambda}

                self.metric_model_exprs=exprs
                self.metric_model_lambdas=lambdas
            else:
                error("Non-single latency not yet supported.",also_stdout=True)
                info("Terminating.")
                assert(False)


            #energy_model_expr, \
            #energy_model_lambda=fit_.polynomial_to_sympy_expression_with_lambda_corrected(energy_model, energy_scaler, energy_best_degree, features)
        else:
            error("buildEnergyAreaMetricModels invalid arguments: type_ =",type_,"norm_ =",norm_)
            info("Terminating.")
            assert(False)
        return self