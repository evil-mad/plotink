# ebb_motion.py
# Motion control utilities for EiBotBoard
# https://github.com/evil-mad/plotink
# 
# Intended to provide some common interfaces that can be used by 
# EggBot, WaterColorBot, AxiDraw, and similar machines.
#
# Version 0.1, Dated January 8, 2016.
#
#
# The MIT License (MIT)
# 
# Copyright (c) 2016 Evil Mad Scientist Laboratories
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ebb_serial


def version():
	return "0.1"	# Version number for this document


def doTimedPause( portName, nPause ):
	if (portName is not None):
		while ( nPause > 0 ):
			if ( nPause > 750 ):
				td = int( 750 )
			else:
				td = nPause
				if ( td < 1 ):
					td = int( 1 ) # don't allow zero-time moves
			ebb_serial.command( portName, 'SM,' + str( td ) + ',0,0\r')		
			nPause -= td
			
			
def sendEnableMotors( portName ):
	if (portName is not None):
		ebb_serial.command( portName, 'EM,1,1\r' )		

def sendDisableMotors( portName ):
	if (portName is not None):
		ebb_serial.command( portName, 'EM,0,0\r')	
		
def QueryPRGButton( portName ):
	if (portName is not None):
		return ebb_serial.query( portName, 'QB\r' )
			
