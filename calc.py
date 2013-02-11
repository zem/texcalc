#!/usr/bin/python -i 

import os
import sys
import re
import subprocess
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


# this funktion converts a number (num) to an iso stringified list
def unum2ISOstring(num, digits=2):
	num=uround(num, digits)
	if isinstance(num, UFloat):
		return [str(num)]
	else: 
		return [str(num)]


#################################################################################################
# File Parsing methods 


# global variables for the evaluate context
evaluate_kontext=globals()
evaluate_line_collect=''
def evaluate_line(line):
	#global evaluate_kontext
	global evaluate_line_collect
	line=re.sub('\(((\d|\.)+)\|((\d|\.)+)\)', 'f((\\1,\\3))', line)
	if re.match('def\s.*:$', line) or ((evaluate_line_collect!='') and (line!='')):
		#print "funktionsdefinition starting collect "+ line
		evaluate_line_collect=evaluate_line_collect+line+"\n"
		return ''
	elif ((line=='') and (evaluate_line_collect!='')):
		exec(evaluate_line_collect+"\n") in evaluate_kontext
		evaluate_line_collect=''
		return ''
	else:
		exec(line) in evaluate_kontext
		expr_list=re.split('=', line)
		return eval(expr_list[0], evaluate_kontext)


# This funktions will be match funktions for the latex tags 
# \val tag
def insert_values_valtag(matchobj):
	tag=matchobj.group(1)
	return tag

# @foo@ tag 
def insert_values_attag(matchobj):
	tag=matchobj.group(1)
	return tag 

# this funktion will parse the line searching for \val tags 
# and at tags calling the replacement functions
def insert_values(line):
	line=re.sub('\@((\w|\d|\,)+)\@', insert_values_attag, line)
	line=re.sub('\\val{((\w|\d|\,)+)}', insert_values_textag, line)
	return line


# this method parses a texfile, puts in the results and 
# inserts the \val{}
def calculate_texfile(filename, texmode='none'):
	#exec('from main import *') in evaluate_kontext
	novalname=filename+".noval.tmp"
	valname=filename+".val.tmp"
	commentchr='%'
	
	i_file = open(filename, "r")
	noval_file = open(novalname, "w")
	val_file = open(valname, "w")
	
	result=''
	for line in i_file:
		line=line.rstrip()
		if re.match(commentchr+'(r)\s', line) :
			print "ignore %r line" + line
			# write this line nowhere 
		# the classic calc c C lines 
		elif (commentchr=="%") and (line=="\\begin{calc}"):
			noval_file.write(line+"\n")
			val_file.write(line+"\n")
			commentchr="#"
		elif (commentchr=="#") and (line=="\\end{calc}"):
			noval_file.write(line+"\n")
			val_file.write(line+"\n")
			commentchr="%"
		elif (commentchr=="#") and (line!="\\end{calc}"):
			noval_file.write(line+"\n")
			val_file.write(line+"\n")
			result=evaluate_line(line)
		elif re.match('\%(calc|c|C)\s', line):
			noval_file.write(line+"\n")
			val_file.write(line+"\n")
			line=re.sub('\%(calc|c|C)\s', '', line)
			line=re.split('\%', line)[0] # yea mod is not working then I know
			result=evaluate_line(line)
		else:
			noval_file.write(line+"\n")
			val_file.write(insert_values(line)+"\n")
		if ( result != '' ): 
			noval_file.write(commentchr+"r "+str(result)+"\n")
			val_file.write(commentchr+"r "+str(result)+"\n")
			result=''
			
	
	val_file.close()
	noval_file.close()
	i_file.close()

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
		print '	usage: '+sys.argv[0]+' [-tex latexcommand] [-C -y] [-c] [-?|-h] [filename]'
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
	calculate_texfile(filename, texmode); 
	os._exit(0)


