TARGET=/usr/local/bin

install: $(TARGET)/calc.py $(TARGET)/texcalc.pl

$(TARGET)/calc.py: calc.py
	cp $< $@

$(TARGET)/texcalc.pl: texcalc.pl
	cp $< $@
