''' Helper functions '''
import yaml,logging,os,warnings,sys

'''Logging'''
log_configured=False
enable_log=False
enable_stdout=True
enable_stderr=True
tqdm_stdout=sys.stdout
tqdm_devnull=open(os.devnull, 'w')
log_path="./safinfer.log"

def get_tqdm_outfile():
    if enable_stdout:
        return tqdm_stdout
    else:
        return tqdm_devnull

def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    warn(f"{category.__name__}: {filename}:{lineno}: {message}")


def log_init(log_path_):
    global log_path
    global log_configured
    
    log_path=log_path_

    try:
        os.remove(log_path)
    except:
        pass

    logging.basicConfig(filename=log_path, level=logging.INFO)
    log_configured=True
    #warnings.simplefilter("default")
    #logging.captureWarnings(True)
    warnings.showwarning = custom_warning_handler


def log_concat(*args):
    return ' '.join(map(str, args))
def crash_if_log_not_configured():
    global log_configured
    if not log_configured:
        print("=> Log not configured. Terminating.")
        assert(False)
def info(*args,also_stdout=False):
    if enable_log:
        crash_if_log_not_configured()
        logging.info(log_concat(*args))
    if enable_stdout and also_stdout:
        print(*args)
def warn(*args,also_stdout=False):
    if enable_log:
        crash_if_log_not_configured()
        logging.warn(log_concat(*args))
    if enable_stdout and also_stdout:
        print(*args)
def error(*args,also_stdout=False):
    if enable_log:
        crash_if_log_not_configured()
        logging.error(log_concat(*args))
    if enable_stderr and also_stdout:
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

def save_yaml(dict_,save_filename):
    with open(save_filename,'w') as save_fp:
        yaml.dump(dict_,save_fp)