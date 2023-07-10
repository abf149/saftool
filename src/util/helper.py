''' Helper functions '''

import yaml

def dirpath_to_importpath(dirpath):
    '''Directory path must be relative to pwd'''
    linux_dirpath=dirpath.replace('\\','/')
    if linux_dirpath[-1]=='/':
        # Remove any training slash
        linux_dirpath=linux_dirpath[0:-1]
    return linux_dirpath.replace('/','.')

def dirpath_to_import_expression(dirpath, py_mod, importas):
    '''Convert a relative directory path into an exec command string for importing a python module under a desired name'''

    return 'global ' + importas + '; from ' + dirpath_to_importpath(dirpath) + ' import ' + py_mod + ' as ' + importas

def load_config_yaml(config_filename):
    """YAML load wrapper

    Keyword arguments:\n
    * config_filename -- the absolute or relative YAML filepath

    Returns: dict
    """
    config=[]

    with open(config_filename,'r') as config_fp:
        config=yaml.safe_load(config_fp)
    
    return config