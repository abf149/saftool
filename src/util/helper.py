''' Helper functions '''
import yaml,logging,os

'''Logging'''
do_log=False
log_path="./safinfer.log"
try:
    os.remove(log_path)
except:
    pass
logging.basicConfig(filename=log_path, level=logging.INFO)
def log_concat(*args):
    return ' '.join(map(str, args))
def info(*args,also_stdout=False):
    if do_log:
        logging.info(log_concat(*args))
    if also_stdout:
        print(*args)
def warn(*args,also_stdout=False):
    if do_log:
        logging.warn(log_concat(*args))
    if also_stdout:
        print(*args)
def error(*args,also_stdout=False):
    if do_log:
        logging.error(log_concat(*args))
    if also_stdout:
        print(*args)

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