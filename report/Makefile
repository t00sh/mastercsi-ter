.PHONY: all clean help

PRESENTATION_TEX = presentation.tex
PRESENTATION_PDF = presentation.pdf

REPORT_PDF = report.pdf
REPORT_TEX = report.tex
REPORT_DEP = appendix.tex chapter-conclusion.tex chapter-https-interception.tex
REPORT_DEP += chapter-intro.tex chapter-sslstrip2.tex chapter-sslstrip-ntp.tex
REPORT_DEP += chapter-sslstrip.tex chapter-state-of-the-art.tex refs.tex


all: $(REPORT_PDF) $(PRESENTATION_PDF)

$(REPORT_PDF): $(REPORT_TEX) $(REPORT_DEP) Makefile
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<

$(PRESENTATION_PDF): $(PRESENTATION_TEX) Makefile
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<
clean:
	rm -f *~ *.nav *.snm *.toc *.out *.aux *.log
	rm -f $(REPORT_PDF) $(PRESENTATION_PDF)


help:
	@ echo "------------------------------------------------------"
	@ echo "Usage:"
	@ echo "  make [all]   # build '$(REPORT_PDF)' and '$(PRESENTATION_PDF)'"
	@ echo "  make clean   # clean temporary files and all pdf"
	@ echo "  make help    # print this help"
	@ echo "------------------------------------------------------"
