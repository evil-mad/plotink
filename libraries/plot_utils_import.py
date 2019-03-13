from importlib import import_module

# this handles importing in two major cases

def from_ink_extensions_import(module_name):
    ''' module_name is the name of the extension, e.g. `inkex` or `simplepath` '''
    module = None
    try:
        # running as a module with imported inkscape extensions source
        # e.g. if you used pip/setup.py
        module = import_module("ink_extensions." + module_name)
    except (ImportError) as ie:
        if 'ink_extensions' in str(ie):
            # if running as script, e.g. as an inkscape extension in inkscape
            module = import_module(module_name)
        else:
            raise ie
    return module
