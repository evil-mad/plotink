from importlib import import_module

# this handles importing in two major cases

def from_dependency_import(module_name):
    ''' module_name ex: "ink_extensions", "ink_extensions.inkex" '''
    module = None
    try:
        # running as an inkscape extension in inkscape
        module = import_module("axidraw_deps." + module_name)
    except (ImportError) as ie:
        # running as a python module with traditionally installed packages
        # e.g. if you used pip or setup.py
        module = import_module(module_name)
    return module
