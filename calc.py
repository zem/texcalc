#!/usr/bin/python -i 

import os
import sys
from math import *
from numpy  import *
import uncertainties
from uncertainties import *
from uncertainties.umath import *

# this variable can be used in files when the value is still not known
VALUE=ufloat((1.0, 0.1)) 

#define some global variables
texmode='none' # should a pdf be generated
latex='pdflatex' # which latex command to use
filename='' # set a filename to the tex file

def f(a, b='na'):
	if (b!='na'):
		return ufloat((a, b))
	else:
		return ufloat(a)

def uround(a, digits=2):
	if isinstance(a, UFloat):
		n=0
		x=std_dev(a)
		while x<10**(digits-1):
			n=n+1
			x=std_dev(a)*10**n
		if x>round(x):
			x=round(x)+1
		else:
			x=round(x)
		x=x/(10**n)
		return f((round(nominal_value(a), n),x))
	else:
		return round(a, digits)

# creates meanval and stderr of an array or a list and returns it as ufloat number
def meanval(a):
	a=array(a)
	mw=a.mean()
	sa=sqrt(((a-mw)**2).mean())
	return f((mw, sa))
	#return [mw, sa]


def calculate_texfile(filename, texmode='none'):
	return
	

################################################################################################
# Main Program

#parse arguments 
arguments=sys.argv[1:]
while len(arguments)>=1:
	arg=arguments.pop(0)
	if (arg=="-q"):
		sys.ps1=""
		sys.ps2=""
	elif (arg=="-t"):
		sys.ps1="ready\n"
		sys.ps2="ready\n"
	elif (arg=="-tex"):
		latex=arguments.pop(0)
	elif (arg=="-c"):
		texmode='generate'
	elif (arg=="-C"):
		if arguments.pop(0) != '-y': 
			print '-C must be followed by -y'
			os._exit(1)
		texmode='replace'
	elif (arg=="-?") or (arg=="-h"):
		print '	usage: calc.py [-tex latexcommand] [-C -y] [-c] [-?|-h] [filename]'
		print '		-tex	configures the latex command to produce pdf files default ist pdflatex'
		print '		-C	-y	exchanges the \\val{xyz} Tags in the .tex file with the calculated values'
		print '		-c		calculates the the file and produces tex'
		print '		-?'
		print '		-h 	prints this help'
		print '			'
		print '	when calles without parameters calc.py will act as a command line calculator '
		os._exit(0)
	else:
		# it is obviously a filename
		filename=arg

#look for file
if (filename != ''): 
	calulate_texfile(filename, texmode); 
	os._exit(0)


