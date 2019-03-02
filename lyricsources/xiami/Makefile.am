xiami_PYTHON = xiami.py

xiamidir = $(pkgdatadir)/lyricsources/xiami


servicedir = $(datarootdir)/dbus-1/services
service_in_files = org.osdlyrics.LyricSourcePlugin.xiami.service.in
service_DATA = $(service_in_files:.service.in=.service)

EXTRA_DIST = \
	$(service_in_files) \
	$(NULL)

$(service_DATA): $(service_in_files)
	@sed -e "s|\@pkgdatadir\@|$(pkgdatadir)|" -e "s|\@PYTHON\@|$(PYTHON)|" $< > $@

CLEANFILES = \
	org.osdlyrics.LyricSourcePlugin.xiami.service \
	$(NULL)
