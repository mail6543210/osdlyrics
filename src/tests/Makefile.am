check_PROGRAMS = \
	ol_osd_window_test \
	ol_player_test \
	ol_config_test \
	ol_color_test \
	ol_path_test \
	ol_utils_cmdline_test \
	ol_metadata_test \
	ol_utils_dbus_test \
	ol_utils_test \
	ol_gussian_blur_test \
	ol_app_info_test \
	ol_lyric_source_test \
	$(NULL)

AM_CPPFLAGS = \
	-DICONDIR='"$(OL_ICONDIR)"' \
	-DGUIDIR='"$(OL_GUIDIR)"' \
	@GTK2_CFLAGS@ \
	@DBUS_GLIB_CFLAGS@ \
	-I$(top_srcdir)/src \
	-I$(top_srcdir)/src/tests \
	$(NULL)

AM_CFLAGS = \
	-Werror -Wall \
	$(NULL)

LDADD = \
	@GTK2_LIBS@ \
	@DBUS_GLIB_LIBS@ \
	-lm \
	$(NULL)

noinst_HEADERS = \
	ol_test_util.h

# Tests
ol_utils_cmdline_test_SOURCES = ol_utils_cmdline_test.c \
	../../src/ol_debug.c \
	../../src/ol_utils_cmdline.c

ol_osd_window_test_SOURCES = ol_osd_window_test.c \
	../../src/ol_osd_window.c \
	../../src/ol_osd_render.c \
	../../src/ol_gussian_blur.c \
	../../src/ol_debug.c \
	../../src/ol_color.c \
	../../src/ol_image_button.c \
	../../src/ol_utils.c

ol_player_test_SOURCES = ol_player_test.c \
	../../src/ol_debug.c \
	../../src/ol_player.c \
	../../src/ol_timeline.c \
	../../src/ol_metadata.c \
	../../src/ol_utils.c \
	$(NULL)

ol_config_test_SOURCES = \
	../../src/ol_debug.c \
	ol_config_test.c \
	../../src/ol_config_proxy.c \
	../../src/ol_marshal.c

ol_color_test_SOURCES = \
	../../src/ol_debug.c \
	ol_color_test.c \
	../../src/ol_color.c

ol_path_test_SOURCES = \
	 ol_path_test.c \
	../../src/ol_debug.c \
	../../src/ol_path_pattern.c \
	../../src/ol_utils.c \
	../../src/ol_metadata.c

ol_metadata_test_SOURCES = \
	ol_metadata_test.c \
	../../src/ol_debug.c \
	../../src/ol_metadata.c \
	../../src/ol_utils.c

ol_utils_dbus_test_SOURCES = \
	ol_utils_dbus_test.c \
	../../src/ol_debug.c \
	../../src/ol_utils_dbus.c

ol_utils_test_SOURCES = \
	ol_utils_test.c \
	../../src/ol_utils.c \
	../../src/ol_debug.c

ol_gussian_blur_test_SOURCES = \
	ol_gussian_blur_test.c \
	../../src/ol_gussian_blur.c \
	../../src/ol_debug.c

ol_app_info_test_SOURCES = \
	ol_app_info_test.c \
	../../src/ol_app_info.c \
	../../src/ol_debug.c \
	$(NULL)

ol_lyric_source_test_SOURCES = \
	ol_lyric_source_test.c \
	../../src/ol_lyric_source.c \
	../../src/ol_debug.c \
	../../src/ol_marshal.c \
	../../src/ol_metadata.c \
	../../src/ol_utils.c \
	$(NULL)
