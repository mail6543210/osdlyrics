http_PYTHON = \
	http-player.py \
	server.py \
	validator.py \
	error.py \
	$(NULL)

httpdir = $(pkgdatadir)/players/http


servicedir = $(datarootdir)/dbus-1/services
service_in_files = org.osdlyrics.PlayerProxy.Http.service.in
service_DATA = $(service_in_files:.service.in=.service)

EXTRA_DIST = \
	$(service_in_files) \
	$(NULL)

$(service_DATA): $(service_in_files)
	@sed -e "s|\@pkgdatadir\@|$(pkgdatadir)|" -e "s|\@PYTHON\@|$(PYTHON)|" $< > $@

CLEANFILES = \
	org.osdlyrics.PlayerProxy.Http.service \
	$(NULL)
