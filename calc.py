#!/usr/bin/python -i 

import sys
from math import *
import uncertainties
from uncertainties import *
from uncertainties.umath import *

def f(a):
	return ufloat(a)

if len(sys.argv)>1 and sys.argv[1]=="-q":
	sys.ps1=""
	sys.ps2=""

if len(sys.argv)>1 and sys.argv[1]=="-t":
	sys.ps1="ready\n"
	sys.ps2="ready\n"


