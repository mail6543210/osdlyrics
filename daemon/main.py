# -*- coding: utf-8 -*-
#
# Copyright (C) 2011  Tiger Soldier
#
# This file is part of OSD Lyrics.
#
# OSD Lyrics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSD Lyrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OSD Lyrics.  If not, see <https://www.gnu.org/licenses/>.
#
from __future__ import print_function
from builtins import super

import logging
logging.basicConfig()
logger = logging.getLogger('Daemon')

import dbus

from osdlyrics import PACKAGE_VERSION
from osdlyrics.app import AlreadyRunningException, App
from osdlyrics.consts import (CONFIG_BUS_NAME, DAEMON_BUS_NAME,
                              DAEMON_INTERFACE, DAEMON_MPRIS2_NAME,
                              DAEMON_OBJECT_PATH, MPRIS2_OBJECT_PATH)
from osdlyrics.metadata import Metadata

import lyrics
import lyricsource
import player

# logger.setLevel(logging.WARNING)


class InvalidClientNameException(Exception):
    """ The client bus name in Hello is invalid
    """

    def __init__(self, name):
        """

        Arguments:
        - `name`: The invalid client bus name
        """
        super().__init__('Client bus name %s is invalid' % name)


class MainApp(App):
    def __init__(self, ):
        super().__init__('Daemon', False)
        self._player = player.PlayerSupport(self.connection)
        self._lyrics = lyrics.LyricsService(self.connection)
        self._connect_metadata_signal()
        self._activate_config()
        self.request_bus_name(DAEMON_MPRIS2_NAME)
        self._daemon_object = DaemonObject(self)
        self._lyricsource = lyricsource.LyricSource(self.connection)
        self._lyrics.set_current_metadata(Metadata.from_dict(
            self._player.current_player.Metadata))

    def _connect_metadata_signal(self, ):
        self._mpris_proxy = self.connection.get_object(DAEMON_BUS_NAME,
                                                       MPRIS2_OBJECT_PATH)
        self._metadata_signal = self._mpris_proxy.connect_to_signal(
            'PropertiesChanged', self._player_properties_changed)

    def _activate_config(self, ):
        try:
            self.connection.activate_name_owner(CONFIG_BUS_NAME)
        except Exception:
            logger.error("Cannot activate config service")

    def _player_properties_changed(self, iface, changed, invalidated):
        if 'Metadata' in changed:
            self._lyrics.set_current_metadata(Metadata.from_dict(
                changed['Metadata']))


def is_valid_client_bus_name(name):
    """Check if a client bus name is valid.

    A client bus name is valid if it starts with `org.osdlyrics.Client.`

    Arguments:
    - `name`: The bus name of client
    """
    return name.startswith('org.osdlyrics.Client.')


class DaemonObject(dbus.service.Object):
    """ DBus Object implementing org.osdlyrics.Daemon
    """

    def __init__(self, app):
        super().__init__(conn=app.connection,
                         object_path=DAEMON_OBJECT_PATH)
        self._watch_clients = {}
        self._app = app

    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='s',
                         out_signature='')
    def Hello(self, client_bus_name):
        logger.info('A new client connected: %s', client_bus_name)
        if is_valid_client_bus_name(client_bus_name):
            if client_bus_name not in self._watch_clients:
                self._watch_clients[client_bus_name] = \
                    self.connection.watch_name_owner(
                        client_bus_name,
                        lambda owner: self._client_owner_changed(
                            client_bus_name, owner))
        else:
            raise InvalidClientNameException(client_bus_name)

    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='',
                         out_signature='s')
    def GetVersion(self):
        return PACKAGE_VERSION

    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='',
                         out_signature='')
    def Quit(self):
        self._app.quit()

    def _client_owner_changed(self, name, owner):
        if owner == '':
            logger.info('Client %s disconnected', name)
            if name in self._watch_clients:
                self._watch_clients[name].cancel()
                del self._watch_clients[name]
            if not self._watch_clients:
                logger.info('All client disconnected, quit the daemon')
                self._app.quit()


def main():
    import os
    logger.setLevel(getattr(logging, os.getenv('DEBUG', 'WARNING')))
    try:
        app = MainApp()
        app.run()
    except AlreadyRunningException:
        print('OSD Lyrics is running')


if __name__ == '__main__':
    main()
