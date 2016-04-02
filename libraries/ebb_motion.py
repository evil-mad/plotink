# ebb_motion.py
# Motion control utilities for EiBotBoard
# https://github.com/evil-mad/plotink
# 
# Intended to provide some common interfaces that can be used by 
# EggBot, WaterColorBot, AxiDraw, and similar machines.
#
# Version 0.6, Dated April 2, 2016.
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
	return "0.6"	# Version number for this document

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

def sendEnableMotors( portName, Res ):
	if (Res < 0):
		Res = 0
	if (Res > 5):
		Res = 5	
	if (portName is not None):
		ebb_serial.command( portName, 'EM,' + str(Res) + ',' + str(Res) + '\r' )
		# If Res == 0, -> Motor disabled
		# If Res == 1, -> 16X microstepping
		# If Res == 2, -> 8X microstepping
		# If Res == 3, -> 4X microstepping
		# If Res == 4, -> 2X microstepping
		# If Res == 5, -> No microstepping

def sendDisableMotors( portName ):
	if (portName is not None):
		ebb_serial.command( portName, 'EM,0,0\r')

def QueryPRGButton( portName ):
	if (portName is not None):
		return ebb_serial.query( portName, 'QB\r' )

def TogglePen( portName ):
	if (portName is not None):
		ebb_serial.command( portName, 'TP\r')

def sendPenUp( portName, PenDelay ):
	if (portName is not None):
		strOutput = ','.join( ['SP,1', str( PenDelay )] ) + '\r'
		ebb_serial.command( portName, strOutput)

def sendPenDown( portName, PenDelay ):
	if (portName is not None):
		strOutput = ','.join( ['SP,0', str( PenDelay )] ) + '\r'
		ebb_serial.command( portName, strOutput)

def doXYAccelMove( portName, deltaX, deltaY, vInitial, vFinal ):
	# Move X/Y axes as: "AM,<initial_velocity>,<final_velocity>,<axis1>,<axis2><CR>"
	# Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
	# On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
	# Note that minimum move duration is 5 ms.
	# Important: Requires firmware version 2.4 or higher.
	if (portName is not None):
		strOutput = ','.join( ['AM', str( vInitial ), str( vFinal ), str( deltaX ), str( deltaY )] ) + '\r'
		ebb_serial.command( portName, strOutput)

def doXYMove( portName, deltaX, deltaY, duration ):
	# Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
	# Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
	# On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
	if (portName is not None):
		strOutput = ','.join( ['SM', str( duration ), str( deltaY ), str( deltaX )] ) + '\r'
		ebb_serial.command( portName, strOutput)

def doABMove( portName, deltaA, deltaB, duration ):
	# Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>"
	# Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
	if (portName is not None):
		strOutput = ','.join( ['XM', str( duration ), str( deltaA ), str( deltaB )] ) + '\r'
		ebb_serial.command( portName, strOutput)				