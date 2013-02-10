#!/usr/bin/python -i 

import sys
from math import *
from numpy  import *
import uncertainties
from uncertainties import *
from uncertainties.umath import *

print sys.argv

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

if len(sys.argv)>1 and sys.argv[1]=="-q":
	sys.ps1=""
	sys.ps2=""

if len(sys.argv)>1 and sys.argv[1]=="-t":
	sys.ps1="ready\n"
	sys.ps2="ready\n"

WERT=f((1.0, 0.1))

def meanval(a):
	a=array(a)
	mw=a.mean()
	sa=sqrt(((a-mw)**2).mean())
	return f((mw, sa))
	#return [mw, sa]

