
all: index.html

index.html: texcalc.de.html
	cp $< $@
	git add * 
	git commit -m "Webpage Generated" *

texcalc.de.html: texcalc.de.tex
	texcalc.py -c -tex htlatex $<

texcalc.de.tex: ../doc/texcalc.de.tex ../doc/texcalc.png
	cp ../doc/texcalc.de.tex $@
	cp -u ../doc/*.png . 

