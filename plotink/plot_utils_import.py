from importlib import import_module
import sys
import os

# this handles importing in two major cases

DEPENDENCY_DIR_NAME = 'axidraw_deps'
DEPENDENCY_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), DEPENDENCY_DIR_NAME)
INK_EXTENSIONS_DIR = os.path.join(DEPENDENCY_DIR, 'ink_extensions')

def from_dependency_import(module_name):
    ''' module_name ex: "ink_extensions", "ink_extensions.inkex"
    module_name must be the name of a module, not a class, function, etc. '''
    module = None

    if os.path.isdir(DEPENDENCY_DIR):
        # running as an inkscape extension in inkscape

        sys.path.insert(0, DEPENDENCY_DIR)

        if 'ink_extensions' in module_name:
            # a special case: inkscape-provided files don't know they are
            # in the ink_extensions module
            sys.path.insert(0, INK_EXTENSIONS_DIR)

        try:
            module = import_module(module_name)
        finally:
            for folder in [DEPENDENCY_DIR, INK_EXTENSIONS_DIR]:
                if folder in sys.path:
                    sys.path.remove(folder)

    else:
        # running as a python module with traditionally installed packages
        # e.g. if you used pip or setup.py
        module = import_module(module_name)

    return module
