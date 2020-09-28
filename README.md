# plotink
Helper routines for Inkscape extensions to drive EggBot, WaterColorBot, AxiDraw, and similar plotter-type machines.

This project is hosted at: https://github.com/evil-mad/plotink

## Overview

These library files are intended to provide a single place to edit routines that are common to the [EggBot extensions for Inkscape](https://github.com/evil-mad/EggBot/), the [WaterColorBot extensions for Inkscape](https://github.com/evil-mad/wcb-ink/), the [AxiDraw extensions for Inkscape](https://github.com/evil-mad/axidraw/), and derivative machines. Hosting these in a single place means less duplication of code, and (more importantly) reduces the number of cases where identical code changes need to be made in multiple places.

The three library files are:

* ebb_serial.py - Routines for communicating with the EiBotBoard by USB serial (PySerial 2.7 + required).
* ebb_motion.py - Common commands for interacting with the robot
* plot_utils.py - Additional helper functions for managing the plot.


## Python version support

New versions, starting with Plotink version 1.1.0 (September 2020), require python 3.5 or newer.

A previous release, [Plotink version 1.0.0](https://pypi.org/project/plotink/1.0.0/), supports python 2.7 as well.


## Logging

This library uses the standard python logging module. Suggested configurations follow.

For manual command of AxiDraw, print info, warnings, and errors to stdout:

```
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
```

For running as an inkscape extension, print errors to inkscape's extension errors log:
```
import logging

logging.basicConfig(level=logging.ERR,
        format='%(message)s'),
        filename = "~/.config/inkscape/extension-errors.log")
```
