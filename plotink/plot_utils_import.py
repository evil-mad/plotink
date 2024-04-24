'''
This module handles importing in two major cases

In one case, the program is being run as a python script/library without inkscape.
Everything can proceed normally.

In the other, NextDraw (or AxiDraw) dependencies are siloed into $DEPENDENCY_DIR_NAME so as not
    to mess with other installations/extensions/etc, and to import them, the import system has
    to be instructed to look in $DEPENDENCY_DIR_NAME first.

In packages that need to use `from_dependency_import` a file named `plot_utils_import.py`
    containing `from plotink.plot_utils_import import * has to be there, so that this importing
    mechanism is available to files in the package with 
    `from plot_utils_import import from_dependency_import`

# to think about this might be a good place to put a blanket import lxml
'''

from importlib import import_module
import sys
import os

DEPENDENCY_DIRS = ['nextdraw_deps', 'axidraw_deps']

def from_dependency_import(module_name):
    ''' module_name ex: "ink_extensions", "ink_extensions.inkex"
    module_name must be the name of a module, not a class, function, etc. '''
    module = None

    for dep_dir in DEPENDENCY_DIRS:
        dependency_dir = os.path.join(os.path.abspath(os.getcwd()), dep_dir)
        ink_extensions_dir = os.path.join(dependency_dir, 'ink_extensions')

        if os.path.isdir(dependency_dir): # running as an inkscape extension in inkscape
            sys.path.insert(0, dependency_dir)
            # inkscape-provided files don't know they are
            # in the ink_extensions module
            sys.path.insert(0, ink_extensions_dir)

            try:
                module = import_module(module_name)
            finally:
                for folder in [dependency_dir, ink_extensions_dir]:
                    if folder in sys.path:
                        sys.path.remove(folder)

    if module is None:
        # running as a python module with traditionally installed packages
        # e.g. if you used pip or setup.py
        module = import_module(module_name)

    return module
