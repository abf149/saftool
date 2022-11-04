''' Helper functions '''

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
