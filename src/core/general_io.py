'''General IO routines'''
import importlib.resources as pkg_resources
from core.helper import info,warn,error
from pathlib import Path
import os

root_package_dir="src/"

'''Library resource access routines'''
def get_abs_path_relative_to_cwd(abs_path):
    return os.path.relpath(abs_path, os.getcwd())

def check_path_type(path):
    if os.path.isdir(path):
        return "directory"
    elif os.path.isfile(path):
        return "file"
    else:
        return "neither"

def get_resource_filepath_or_dir(repo_filepath):

    #repo_filepath_obj=Path(repo_filepath)
    repo_dir=Path(__file__).parent.parent.parent

    return os.path.join(repo_dir,repo_filepath)

    #print(repo_filepath_obj.relative_to(this_dir))
    #print("asdf:",os.path.join(repo_dir,repo_filepath))
    #assert(False)

    def to_dotted_path(file_path, root_package_dir):
        relative_path = os.path.relpath(file_path, root_package_dir)
        module_path, _ = os.path.splitext(relative_path)
        dotted_path = module_path.replace(os.sep, '.')
        return dotted_path

    path_prefix, base_filename = os.path.split(repo_filepath)
    dotted_path = to_dotted_path(path_prefix, root_package_dir)

    try:
        with pkg_resources.path(dotted_path, base_filename) as file_path:
            warn("Mapping repository filepath",repo_filepath,"to absolute path",str(file_path))
            return file_path
    except Exception:
        error("Could not map repository filepath",repo_filepath,"to absolute path.",also_stdout=True)
        info("Terminating.")
        assert(False)