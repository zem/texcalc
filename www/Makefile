
all: index.html 

index.html: texcalc.de.html texcalc.de.pdf
	cp $< $@
	git add * 
	git commit -m "Webpage Generated" *

texcalc.de.pdf: texcalc.de.tex
	texcalc.py -c $<

texcalc.de.html: texcalc.de.tex
	texcalc.py -c -tex htlatex $<

texcalc.de.tex: ../doc/texcalc.de.tex ../doc/texcalc.png
	cp ../doc/texcalc.de.tex $@
	cp -u ../doc/*.png . 

