TARGET=/usr/local/bin
TEXMFTARGET=${HOME}/texmf/tex/latex/phunivie

install: $(TARGET)/texcalc.pl

$(TEXMFTARGET)/phunivie.sty: phunivie.sty
	mkdir -p $(TEXMFTARGET)
	cp $< $@

$(TARGET)/texcalc.py: texcalc.pl
	cp $< $@
