from importlib import import_module
import sys
import os

# this handles importing in two major cases

dependency_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'axidraw_deps')

def from_dependency_import(module_name):
    ''' module_name ex: "ink_extensions", "ink_extensions.inkex" '''
    module = None
    try:
        # running as a python module with traditionally installed packages
        # e.g. if you used pip or setup.py
        module = import_module(module_name)
    except (ImportError) as ie:
        if module_name in str(ie):
            # if running as script, e.g. as an inkscape extension in inkscape
            if dependency_dir not in sys.path:
                sys.path.append(dependency_dir)
            module = import_module(module_name)
        else:
            raise ie
    return module
