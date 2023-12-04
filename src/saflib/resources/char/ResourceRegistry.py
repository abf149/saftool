import util.notation.characterization as ch_
from util.helper import info,warn,error

charactization_table_dict={}

def registerCharacterizationTable(id_=None,filepath=""):
    '''
    Arguments:\n
    - id_ -- Identifying for the characterization table
    - filepath -- Full path to characterization table CSV file. Base filename must be primitives_table.csv
    '''
    global charactization_table_dict
    if id_ is None:
        # Default id is filename
        if 'src/accelergy/data/primitives_table.csv' in filepath:
            # Handle special case where the filepath is the repo-internal default characterization table
            # and no id is specified.
            id_='accelergy/data/primitives_table.csv'
        else:
            id_ = filepath
        # Alternatively - random id
        #import uuid
        #id_ = str(uuid.uuid4())
    info('- Loading characterization table with id =',id_,", filepath =",filepath,'...')
    charactization_table_dict[id_]=ch_.CharacterizationTableLoader(filepath)
    charactization_table_dict[id_].loadCharacterizationTable()
    info('- => Done.')

def registerCharacterizationTables(id_list=None,filepath_list=[]):
    if id_list is None:
        id_list=filepath_list

    for id_,filepath in zip(id_list,filepath_list):
        registerCharacterizationTable(id_,filepath)

def getCharacterizationTable(id_):
    '''
    Get a characterization table by id.\n\n

    Arguments:\n
    - id_ -- characterization table ID
    '''
    global charactization_table_dict
    return charactization_table_dict[id_]

def getCharacterizationTablesDict():
    '''
    Get all characterization tables as dict.\n\n
    
    Returns: dict[id str] = CharacterizationTableLoader instance
    '''
    global charactization_table_dict
    return charactization_table_dict

'''
ctbl=getCharacterizationTable('accelergy/data/primitives_table.csv')
ctv,rgx=ctbl.getViewMatchingNameExpression \
    ('BidirectionalBitmaskIntersectDecoupled_metaDataWidth$(u)',['u'])

#print(ctv)

sv=ctv.getSupportedVariableValues()
cmbs=ctv.getSupportedVariableValueCombos()

#print(sv)
#print(cmbs)

#ctv2,rgx2=ctbl.getViewMatchingNameExpression \
#    ('BidirectionalBitmaskIntersectDecoupled_metaDataWidth$(u)',['u'],'And(clock > 1.5, clock <= 5.5)','2*critical_path_length')

#print( \
#ctv2.getAggregatedRowsListByNameAndFilter(name_='BidirectionalBitmaskIntersectDecoupled_metaDataWidth128', \
#                                          row_filter_expression=None, 
#                                          aggregation_expression='2*critical_path_length') \
#)

#.latencyIndependentVariableExpression('2*critical_path_length') \
#.latencyRangeExpression('And(latency > 1.5, latency <= 5.5)') \

#,rtl_loader,hcl_loader,sim_loader
mW_to_W=0.001
ns_to_s=1.0e-9
# critical_path_clock_latency
# .latencyIndependentVariableExpression('critical_path_length') \
# .latencyParameterId('clock') \
cfxn=ch_.CharacterizationMetricModel('test_fxn',ctbl) \
        .parentComponentUri('f.g') \
        .nameExpression('BidirectionalBitmaskIntersectDecoupled_metaDataWidth$(u)',['u']) \
        .symbolMap({'u':'@x','v':'@y'}) \
        .inheritParameters({'clock':'5ns','technology':'45nm'}) \
        .latencyIndependentVariableExpression('critical_path_clock_latency') \
        .latencyRangeExpression('And(latency<=2,latency>=0)')\
        .rowEnergyMetricFromRowPowerMetricExpression('combinational_total_power+register_total_power+clock_network_total_power') \
        .rowAreaMetricExpression('Combinational_Area') \
        .buildSymbolMap() \
        .buildSymList() \
        .buildCharacterizationTableView() \
        .buildSupportedConfigurations() \
        .buildSupportedSymbolValuesConstraints() \
        .buildSupportedSymbolValueCombosConstraints() \
        .buildRowEnergyMetricExpressionIfDerivedFromPower() \
        .buildRowEnergyLambda() \
        .buildRowAreaLambda() \
        .buildEnergyAreaLatencyTable() \
        .buildEnergyAreaMetricModels()
        #.build('poly')

#print(list(cfxn.getEnergyAreaLatencyDict().keys()))
#x=cfxn.getEnergyAreaLatencyDataset()
#print(len(x))
#print(cfxn.getEnergyAreaLatencyTableIndependentVariableNames())
#print(cfxn.getEnergyAreaLatencyDatasetColumnNames())
#print(cfxn.getEnergyAreaLatencyDataset())

#print(cfxn.getFunctionId())

#energy_expr=cfxn.getEnergyMetricExpression()
#energy_lambda=cfxn.getEnergyMetricLambda()
#area_expr=cfxn.getAreaMetricExpresion()
#area_lambda=cfxn.getAreaMetricLambda()
#rtl_str=cfxn.getRTL(sym_dict)
#hcl_str=cfxn.getHCL(sym_dict)
#sim_loader=cfxn.getSim(sym_dict)

#print(ctv2.view_dict)

assert(False)
'''