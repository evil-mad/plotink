from importlib import import_module
import sys
import os

# this handles importing in two major cases

DEPENDENCY_DIR_NAME = 'axidraw_deps'
DEPENDENCY_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), DEPENDENCY_DIR_NAME)

def from_dependency_import(module_name):
    ''' module_name ex: "ink_extensions", "ink_extensions.inkex"
    module_name must be the name of a module, not a class, function, etc. '''
    module = None

    if os.path.isdir(DEPENDENCY_DIR):
        # running as an inkscape extension in inkscape

        old_path = sys.path[0] # this should be working directory, e.g. inkscape/extensions
        sys.path[0] = DEPENDENCY_DIR

        try:
            module = import_module(module_name)
        finally:
            sys.path[0] = old_path

    else:
        # running as a python module with traditionally installed packages
        # e.g. if you used pip or setup.py
        module = import_module(module_name)

    return module
