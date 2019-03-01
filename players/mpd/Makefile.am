mpd_PYTHON = \
        mpd_proxy.py \
        $(NULL)

mpddir = $(pkgdatadir)/players/mpd


servicedir = $(datadir)/dbus-1/services
service_in_files = org.osdlyrics.PlayerProxy.Mpd.service.in
service_DATA = $(service_in_files:.service.in=.service)

EXTRA_DIST = \
        $(service_in_files) \
        $(NULL)

$(service_DATA): $(service_in_files)
	@sed -e "s|\@pkgdatadir\@|$(pkgdatadir)|" -e "s|\@PYTHON\@|$(PYTHON)|" $< > $@

CLEANFILES = \
        org.osdlyrics.PlayerProxy.Mpd.service \
        $(NULL)
.PHONY: $(service_DATA)
