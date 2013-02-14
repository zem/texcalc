# For installation in Home directory use 
# PREFIX=$HOME SHARE=$HOME
#
# For Packaging use PREFIX=/whatever/usr
#

PREFIX=/usr/local
SHARE=${PREFIX}/share

TARGET=${PREFIX}/bin
TEXMF=${SHARE}/texmf/tex/latex/phunivie

install: $(TARGET)/texcalc.py

$(TEXMF)/phunivie.sty: phunivie.sty
	mkdir -p $(TEXMF)
	cp $< $@
	mktexlsr

$(TARGET)/texcalc.py: texcalc.py
	cp $< $@
