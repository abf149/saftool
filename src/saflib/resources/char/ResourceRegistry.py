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