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

registerCharacterizationTable(filepath='accelergy/data/primitives_table.csv')
ctbl=getCharacterizationTable('accelergy/data/primitives_table.csv')
ctv,rgx=ctbl.getViewMatchingNameExpression \
    ('BidirectionalBitmaskIntersectDecoupled_metaDataWidth$(u)',['u'])

#print(ctv)

sv=ctv.getSupportedVariableValues()
cmbs=ctv.getSupportedVariableValueCombos()

#print(sv)
#print(cmbs)

ctv2,rgx2=ctbl.getViewMatchingNameExpression \
    ('BidirectionalBitmaskIntersectDecoupled_metaDataWidth$(u)',['u'],'And(clock > 1.5, clock <= 5.5)','2*critical_path_length')

print( \
ctv2.getAggregatedRowsListByNameAndFilter(name_='BidirectionalBitmaskIntersectDecoupled_metaDataWidth128', \
                                          row_filter_expression=None, 
                                          aggregation_expression='2*critical_path_length') \
)

cfxn=ch_.CharacterizationFunction('test_fxn',ctv2)

#print(ctv2.view_dict)

assert(False)