.PHONY: all clean help

PRESENTATION_TEX = presentation.tex
PRESENTATION_PDF = presentation.pdf
PRESENTATION_DEP = prez-conclusion.tex prez-environment.tex prez-etat-art.tex
PRESENTATION_DEP += prez-http-https.tex prez-https-interception.tex
PRESENTATION_DEP += prez-introduction.tex prez-plan.tex prez-sslstrip2.tex
PRESENTATION_DEP += prez-sslstrip-ntp.tex prez-sslstrip.tex

all: $(PRESENTATION_PDF)

$(PRESENTATION_PDF): $(PRESENTATION_TEX) $(PRESENTATION_DEP) Makefile
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<
clean:
	rm -f *~ *.nav *.snm *.toc *.out *.aux *.log
	rm -f $(PRESENTATION_PDF)


help:
	@ echo "------------------------------------------------------"
	@ echo "Usage:"
	@ echo "  make [all]   # build '$(PRESENTATION_PDF)'"
	@ echo "  make clean   # clean temporary files and pdf"
	@ echo "  make help    # print this help"
	@ echo "------------------------------------------------------"
