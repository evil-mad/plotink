# plotink
Python helper routines for driving AxiDraw, EggBot, WaterColorBot, and similar plotter-based machines.

Source code and issue tracker are hosted [at github](https://github.com/evil-mad/plotink).


## Installation

Releases are available [on PyPI](https://pypi.org/project/plotink/).

To install the latest release, use `pip install plotink`


## Overview

These library files are intended to provide a single place to edit routines that are common to the [EggBot extensions for Inkscape](https://github.com/evil-mad/EggBot/), the [WaterColorBot extensions for Inkscape](https://github.com/evil-mad/wcb-ink/), the [AxiDraw extensions for Inkscape](https://github.com/evil-mad/axidraw/), and derivative machines. Hosting these in a single place means less duplication of code, and (more importantly) reduces the number of cases where identical code changes need to be made in multiple places.

The library files are:

* ebb_serial.py - General routines for communicating with the EiBotBoard by USB serial.
* ebb_motion.py - Motion-related routines for interacting with the robot.
* plot_utils.py - Additional helper functions for managing the plot.


## Python version support

New versions, starting with Plotink version 1.1.0 (September 2020), require python 3.5 or newer.

A previous release, [Plotink version 1.0.1](https://pypi.org/project/plotink/1.0.1/), supports python 2.7 as well.

## Logging

This library uses the standard python logging module. Suggested configurations follow.

For stand-alone machine control, print info, warnings, and errors to stdout:

```
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
```

For running as an Inkscape extension, print errors to Inkscape's extension errors log:
```
import logging

logging.basicConfig(level=logging.ERR,
        format='%(message)s'),
        filename = "~/.config/inkscape/extension-errors.log")
```
