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
job=[] # sets the filename of a latex jobfile 

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

# rounds up all the stringified 
# values to eliminate the exponent
def KillExp(num):
	while num[2] != 0: 
		if num[2] > 0: 
			num[2]=num[2]-1
			if len(num[1]) > 0:
				num[0]=num[0]+num[1][1]
				if len(num[1]) > 1: 
					num[1]=num[1][2:]
				else:
					num[1]=''
			else:
				num[0]=num[0]+'0'
		else:  # num[2] < 0 
			num[2]=num[2]+1
			if len(num[0]) > 0:
				num[1]=num[0][-1]+num[1]
				if len(num[0]) > 1: 
					num[0]=num[0][:-1]
				else:
					num[0]=''
			else:
				num[1]='0'+num[1]
	return num
	

# makes the third element (exponent) of the list 
# numerical integer 
def ExpToNum(num):
	if (len(num)<3): 
		num.append(0)
	else:
		num[2]=int(num[2])
	return num

# this funktion converts a number (num) to an iso stringified list
def unum2TEXstring(num, digits=2):
	num=uround(num, digits)
	if isinstance(num, UFloat):
		# ok we want to round to all the the 
		# significant digits
		#
		# ok, this part splits up the numbers to a stringified list, 
		# makes the exponent numerical and eliminates it 
		val=KillExp(ExpToNum(re.split('\\.|e', str(nominal_value(num)))))
		unc=KillExp(ExpToNum(re.split('\\.|e', str(std_dev(num)))))
		#
		# Ok, we can now count the significant digits 
		while ( len(re.sub('^0+', '', unc[0]+unc[1])) < digits ):
			unc[1]=unc[1]+'0'
		while ( len(val[1]) < len(unc[1]) ):
			val[1]=val[1]+'0'
		if unc[0]=='': unc[0]='0'
		if val[0]=='': val[0]='0'
		return '('+val[0]+','+val[1]+' \\pm '+unc[0]+','+unc[1]+')'
	else: 
		return str(num)


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
		print "funktionsdefinition starting collect "+ line
		evaluate_line_collect=evaluate_line_collect+line+"\n"
		return ''
	elif ((line=='') and (evaluate_line_collect!='')):
		print "evaluating block:"
		print evaluate_line_collect
		exec(evaluate_line_collect+"\n") in evaluate_kontext
		evaluate_line_collect=''
		return ''
	else:
		print "evaluating line: "+line
		exec(line) in evaluate_kontext
		expr_list=re.split('=', line)
		ret=eval(expr_list[0], evaluate_kontext)
		print "return value: ", ret
		return ret


# This funktions will be match funktions for the latex tags 
# \val tag
def insert_values_valtag(matchobj):
	TEXstring=unum2TEXstring(evaluate_line(matchobj.group(1)))
	return TEXstring

def insert_values_valtaglen(matchobj):
	TEXstring=unum2TEXstring(evaluate_line(matchobj.group(2)), int(matchobj.group(1)))
	return TEXstring

# @foo@ tag 
def insert_values_attag(matchobj):
	tag=re.split(',', matchobj.group(1))
	print "processing tag: ", tag
	if len(tag)<2:
		TEXstring=unum2TEXstring(evaluate_line(tag[0]))
	else: 
		TEXstring=unum2TEXstring(evaluate_line(tag[0]),int(tag[1]))
	return TEXstring

# this funktion will parse the line searching for \val tags 
# and at tags calling the replacement functions
def insert_values(line):
	line=re.sub('\@((\w|\d|\,)+)\@', insert_values_attag, line)
	line=re.sub('\\\\val{(.+?)}', insert_values_valtag, line)
	line=re.sub('\\\\val\\[(\d+)\\]{(.+?)}', insert_values_valtaglen, line)
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
			#print "ignore %r line" + line
			pass
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
		elif re.match('\%(calc|c|C)\s', line) or re.match('\%(calc)', line):
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
	os.unlink(filename)
	if (texmode!='none'):
		os.link(valname, filename)
		latexcmd=re.split('\s+', latex)
		latexcmd.append(filename)
		if subprocess.call(latexcmd) != 0: os._exit(1)
		if subprocess.call(latexcmd) != 0: os._exit(1)
		if (texmode!='replace'):
			os.unlink(filename)
	if (texmode!='replace'):
		os.link(novalname, filename)
	os.unlink(valname)
	os.unlink(novalname)
	return

def usage():
	print '	usage: '+sys.argv[0]+' [-tex latexcommand] [-C -y] [-c] [-?|-h] [filename] [-job jobname variable digits]'
	print '		-tex	configures the latex command to produce pdf files default ist pdflatex'
	print '		-C	-y	exchanges the \\val{xyz} Tags in the .tex file with the calculated values'
	print '		-c		calculates the the file and produces tex'
	print '		-job jobname variable digits is for an automated call from within latex'
	print '		-?'
	print '		-h 	prints this help'
	print '			'
	print '	when calles without parameters calc.py will act as a command line calculator '


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
	elif (arg=="-job"):
		job.append(arguments.pop(0))
		while len(arguments)>=1:
			job.append(arguments.pop(0))
	elif (arg=="-c"):
		texmode='generate'
	elif (arg=="-C"):
		if arguments.pop(0) != '-y': 
			print '-C must be followed by -y'
			os._exit(1)
		texmode='replace'
	elif (arg=="-?") or (arg=="-h"):
		usage()
		os._exit(0)
	else:
		# it is obviously a filename
		filename=arg

if (len(job)>0):
	num=1
	jobfile=job.pop(0)
	currjob=jobfile+".calc."+str(num)+".py"
	while (os.path.isfile(currjob)):
		execfile(currjob, evaluate_kontext)
		num=num+1
		currjob=jobfile+".calc."+str(num)+".py"
	exec("print unum2TEXstring(uround("+job[0]+","+job[1]+"),"+job[1]+")") in evaluate_kontext
	os._exit(0)
	
#look for file
if (filename != ''): 
	calculate_texfile(filename, texmode); 
	os._exit(0)

print "                 ++++++++++++++++++++++++"
print "                 +  Welcome to TeXcalc! +"
print "                 ++++++++++++++++++++++++"
print 
print "TeXcalc is a full proof command line calculator written in python, which can "
print "calculate everythig, you think about especially if you think about"
print "  _uncertainties_!"
print 
print "for example, try: "
print "              sin(f(23.005 , 0.023)+f(42.005 , 0.23))*23.0"
print 
print "since this is a python prompt, it can do everything python can do. "
print "you can also parse calculations in a latex file enclosed by a calc environment"
print "and you can automatically insert the results with \\val{x} tags into your pdf"
print "look at the help, (texcalc.py -h) for more information about the usage. good luck!"
print 
