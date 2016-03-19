# plot_utils.py
# Common geometric plotting utilities for EiBotBoard
# https://github.com/evil-mad/plotink
# 
# Intended to provide some common interfaces that can be used by 
# EggBot, WaterColorBot, AxiDraw, and similar machines.
#
# Version 0.4, Dated February 22, 2016.
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

from math import sqrt
import cspsubdiv
from bezmisc import *

def version():
	return "0.3"	# Version number for this document

def distance( x, y ):
	'''
	Pythagorean theorem!
	'''
	return sqrt( x * x + y * y )

def parseLengthWithUnits( str ):
	'''
	Parse an SVG value which may or may not have units attached
	This version is greatly simplified in that it only allows: no units,
	units of px, and units of %.  Everything else, it returns None for.
	There is a more general routine to consider in scour.py if more
	generality is ever needed.
	'''
	u = 'px'
	s = str.strip()
	if s[-2:] == 'px':
		s = s[:-2]
	elif s[-2:] == 'in':		
		s = s[:-2]
		u = 'in'		
	elif s[-2:] == 'mm':		
		s = s[:-2]
		u = 'mm'			
	elif s[-2:] == 'cm':		
		s = s[:-2]
		u = 'cm'			
	elif s[-1:] == '%':
		u = '%'
		s = s[:-1]

	try:
		v = float( s )
	except:
		return None, None

	return v, u


def getLength( altself, name, default ):
	'''
	Get the <svg> attribute with name "name" and default value "default"
	Parse the attribute into a value and associated units.  Then, accept
	no units (''), units of pixels ('px'), and units of percentage ('%').
	'''
	str = altself.document.getroot().get( name )

	if str:
		v, u = parseLengthWithUnits( str )
		if not v:
			# Couldn't parse the value
			return None
		elif ( u == '' ) or ( u == 'px' ):
			return v
		elif  u == 'in' :
			return (float( v ) * 90.0)		#90 px per inch, as of Inkscape 0.91
		elif u == 'mm':
			return (float( v ) * 90.0 / 25.4)
		elif u == 'cm':
			return (float( v ) * 90.0 / 2.54)
		elif u == '%':
			return float( default ) * v / 100.0
		else:
			# Unsupported units
			return None
	else:
		# No width specified; assume the default value
		return float( default )

def getLengthInches( altself, name ):
	'''
	Get the <svg> attribute with name "name" and default value "default"
	Parse the attribute into a value and associated units.  Then, accept
	units of inches ('in'), millimeters ('mm'), or centimeters ('cm')
	'''
	str = altself.document.getroot().get( name )
	if str:
		v, u = parseLengthWithUnits( str )
		if not v:
			# Couldn't parse the value
			return None
		elif  u == 'in' :
			return v
		elif u == 'mm':
			return (float( v ) / 25.4)
		elif u == 'cm':
			return (float( v ) / 2.54)
		else:
			# Unsupported units
			return None

def subdivideCubicPath( sp, flat, i=1 ):
	"""
	Break up a bezier curve into smaller curves, each of which
	is approximately a straight line within a given tolerance
	(the "smoothness" defined by [flat]).

	This is a modified version of cspsubdiv.cspsubdiv(). I rewrote the recursive
	call because it caused recursion-depth errors on complicated line segments.
	"""

	while True:
		while True:
			if i >= len( sp ):
				return

			p0 = sp[i - 1][1]
			p1 = sp[i - 1][2]
			p2 = sp[i][0]
			p3 = sp[i][1]

			b = ( p0, p1, p2, p3 )

			if cspsubdiv.maxdist( b ) > flat:
				break
			i += 1

		one, two = beziersplitatt( b, 0.5 )
		sp[i - 1][2] = one[1]
		sp[i][0] = two[2]
		p = [one[2], one[3], two[1]]
		sp[i:1] = [p]


def checkLimits( value, lowerBound, upperBound ):
	#Check machine size limit; truncate at edges
	if (value > upperBound):
		return upperBound, True
	if (value < lowerBound):
		return lowerBound, True	
	return value, False	
	
	
def vFinal_Vi_A_Dx(Vinitial,Acceleration,DeltaX):
	'''
	Kinematic calculation: Final velocity with constant linear acceleration. 
	
	Calculate and return the (real) final velocity, given an initial velocity, 
		acceleration rate, and distance interval.

	Uses the kinematic equation Vf^2 = 2 a D_x + Vi^2, where 
			Vf is the final velocity, 
			a is the acceleration rate, 
			D_x (delta x) is the distance interval, and
			Vi is the initial velocity.	
			
	We are looking at the positive root only-- if the argument of the sqrt
		is less than zero, return -1, to indicate a failure.		
	'''		
	FinalVSquared = ( 2 * Acceleration * DeltaX ) +	( Vinitial * Vinitial )
	if (FinalVSquared > 0):
		return sqrt(FinalVSquared)	
	else:
		return -1		

def vInitial_VF_A_Dx(VFinal,Acceleration,DeltaX):
	'''
	Kinematic calculation: Maximum allowed initial velocity to arrive at distance X
	with specified final velocity, and given maximum linear acceleration. 
	
	Calculate and return the (real) initial velocity, given an final velocity, 
		acceleration rate, and distance interval.

	Uses the kinematic equation Vi^2 = Vf^2 - 2 a D_x , where 
			Vf is the final velocity, 
			a is the acceleration rate, 
			D_x (delta x) is the distance interval, and
			Vi is the initial velocity.	
			
	We are looking at the positive root only-- if the argument of the sqrt
		is less than zero, return -1, to indicate a failure.	
	'''		
	IntialVSquared = ( VFinal * VFinal )  - ( 2 * Acceleration * DeltaX )
	if (IntialVSquared > 0):
		return sqrt(IntialVSquared)	
	else:
		return -1		


def dotProductXY( inputVectorFirst, inputVectorSecond):
	temp = inputVectorFirst[0] * inputVectorSecond[0] + inputVectorFirst[1] * inputVectorSecond[1]
	if (temp > 1):
		return 1
	elif (temp < -1):
		return -1
	else:
		return temp 	
