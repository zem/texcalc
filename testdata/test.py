def tstr(unum, string, digits=2):
	gen_str=unum2TEXstring(unum, digits)
	print "Testing ", unum
	if (gen_str != string): 
		print "Failed!"
		print "Should be ", string
		print "is ", gen_str
		os._exit(1)
	return

tstr(f(1.732, 0.093), '(1,73 \pm 0,10)', 1)
tstr(f(1234, 120), '(1230 \pm 120)')
tstr(f(17.32, 1.39381), '(17,3 \pm 1,4)')
tstr(f(1.732, 0.0093), '(1,7320 \pm 0,0093)')
