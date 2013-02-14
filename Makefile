# For installation in Home directory use 
# PREFIX=$HOME SHARE=$HOME
#
# For Packaging use PREFIX=/whatever/usr
#

PREFIX=/usr/local
SHARE=${PREFIX}/share

TARGET=${PREFIX}/bin
TEXMF=${SHARE}/texmf/tex/latex/texcalc

install: $(TEXMF)/texcalc.sty $(TARGET)/texcalc.py
install-contrib: $(TEXMF)/anfpralayout.sty $(TEXMF)/physictools.sty 

$(TEXMF)/%.sty: contrib/%.sty
	mkdir -p $(TEXMF)
	cp $< $@
	mktexlsr

$(TEXMF)/%.sty: %.sty
	mkdir -p $(TEXMF)
	cp $< $@
	mktexlsr

$(TARGET)/%.py: %.py
	cp $< $@
