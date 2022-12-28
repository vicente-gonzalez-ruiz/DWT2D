haar_modulus.svg:	DWT_filters_study.ipynb
	jupyter nbconvert --to notebook --execute DWT_filters_study.ipynb
SVGs += haar_modulus.svg
TMPs += haar_modulus.pdf

haar_phase.svg:	DWT_filters_study.ipynb
	jupyter nbconvert --to notebook --execute DWT_filters_study.ipynb
SVGs += haar_phase.svg
TMPs += haar_phase.pdf

db5_modulus.svg:	DWT_filters_study.ipynb
	jupyter nbconvert --to notebook --execute DWT_filters_study.ipynb
SVGs += db5_modulus.svg
TMPs += db5_modulus.pdf

db5_phase.svg:	DWT_filters_study.ipynb
	jupyter nbconvert --to notebook --execute DWT_filters_study.ipynb
SVGs += db5_phase.svg
TMPs += db5_phase.pdf

dwt_lena.png:	DWT_lena.ipynb
	jupyter nbconvert --to notebook --execute DWT_lena.ipynb
PNGs += dwt_lena.png
#SVGs += dwt_lena.svg
TMPs += dwt_lena.pdf

DWT_scaled.pdf:	DWT.pdf
	gs -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=1280 -dPDFSETTINGS=/default -dNOPAUSE -dQUIET -dBATCH -sOutputFile=DWT_scaled.pdf DWT.pdf
PDFs += DWT_scaled.pdf
#TMPs += DWT_scaled.pdf

#DWT_scaled.svg:	DWT_scaled.pdf
#	rsvg-convert DWT_scaled.pdf > DWT_scaled.svg
SVGs += DWT_scaled.svg
#TMPs += DWT_scaled.svg

include $(HOME)/Makefile_templates/Makefile

