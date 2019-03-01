bin_SCRIPTS = osdlyrics-create-lyricsource

osdlyricstoolsdir = $(pkgdatadir)/tools
osdlyricstools_PYTHON = \
	create-lyricsource.py \
	$(NULL)

osdlyrics-create-lyricsource: osdlyrics-create-lyricsource.in
	@sed -e "s|\@pkgdatadir\@|$(pkgdatadir)|" -e "s|\@PYTHON\@|$(PYTHON)|" $< > $@

CLEANFILES = \
	osdlyrics-create-lyricsource \
	$(NULL)
.PHONY: osdlyrics-create-lyricsource
