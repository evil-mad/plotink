'''
plot_utils_import.py

Import utility for plotink, https://github.com/evil-mad/plotink

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


See __version__ below for version information


The MIT License (MIT)

Copyright (c) 2024 Windell H. Oskay, Bantam Tools

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__version__ = '0.2'  # Dated 2024-5-13


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
