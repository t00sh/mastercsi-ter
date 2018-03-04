.PHONY: all clean help

REPORT_PDF = report.pdf
REPORT_TEX = report.tex
REPORT_DEP = refs.tex
REPORT_DEP += chapter-state-of-the-art.tex chapter-sslstrip.tex


all: $(REPORT_PDF)

$(REPORT_PDF): $(REPORT_TEX) $(REPORT_DEP) Makefile
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<

clean:
	rm -f *~ *.toc *.out *.aux *.log $(REPORT_PDF)


help:
	@ echo "------------------------------------------------------"
	@ echo "Usage:"
	@ echo "  make [all]   # build '$(REPORT_PDF)'"
	@ echo "  make clean   # clean temporary files and $(REPORT_PDF)"
	@ echo "  make help    # print this help"
	@ echo "------------------------------------------------------"
