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
# along with OSD Lyrics.  If not, see <http://www.gnu.org/licenses/>. 
#/

import dbus
import dbus.service
import dbus.types
import osdlyrics
import osdlyrics.dbusext

from dbus.mainloop.glib import DBusGMainLoop
from osdlyrics.player_proxy import *

PROXY_NAME = 'Mpris2'
BUS_NAME = osdlyrics.PLAYER_PROXY_BUS_NAME_PREFIX + PROXY_NAME
PROXY_IFACE = osdlyrics.PLAYER_PROXY_INTERFACE
PROXY_PATH = osdlyrics.PLAYER_PROXY_OBJECT_PATH_PREFIX + PROXY_NAME
MPRIS2_PREFIX = 'org.mpris.MediaPlayer2.'
MPRIS2_IFACE = 'org.mpris.MediaPlayer2.Player'
MPRIS2_PATH = '/org/mpris/MediaPlayer2'
MPRIS1_IFACE = osdlyrics.MPRIS1_INTERFACE

def player_info_from_name(name):
    """ Returns a dict representing a player info by the given name
    """
    return PlayerInfo(name)

class ProxyObject(BasePlayerProxy):
    """ The DBus object for MPRIS2 player proxy
    """
    
    def __init__(self):
        """
        """
        super(ProxyObject, self).__init__('Mpris2')

    def _get_player_from_bus_names(self, names):
        """ Returns list of `PlayerInfo` objects according to names.

        The bus names in names with prefix of MPRIS2_PREFIX will be treated as MPRIS2
        players. The suffix of these names will be treated as player name
        
        Arguments:
        - `names`: list of bus names
        """
        return [player_info_from_name(name[len(MPRIS2_PREFIX):]) for name in names
                if name.startswith(MPRIS2_PREFIX)]

    def do_list_active_players(self):
        return self._get_player_from_bus_names(self.connection.list_names());

    def do_list_supported_players(self):
        return self.do_list_activatable_players()

    def do_list_activatable_players(self):
        players = self._get_player_from_bus_names(self.connection.list_activatable_names())
        return players

    def do_connect_player(self, player_name):
        player = Mpris2Player(self, player_name)
        return player

class Mpris2Player(BasePlayer):
    def __init__(self, proxy, player_name):
        super(Mpris2Player, self).__init__(proxy,
                                           player_name)
        self._signal_math = None
        self._name_watch = None
        try:
            self._player = dbus.Interface(self.connection.get_object(MPRIS2_PREFIX + player_name,
                                                                     MPRIS2_PATH),
                                          MPRIS2_IFACE)
            mpris2_object_path = MPRIS2_PREFIX + player_name
            self._player_prop = dbus.Interface(self.connection.get_object(mpris2_object_path,
                                                                          MPRIS2_PATH),
                                               dbus.PROPERTIES_IFACE)
            self._signal_math = self._player_prop.connect_to_signal('PropertiesChanged',
                                                                    self._player_properties_changed)
            self._name_watch = self.connection.watch_name_owner(mpris2_object_path,
                                                                self._name_lost)
        except:
            self.disconnect()

    def _name_lost(self, name):
        if len(name) > 0:
            return
        self.disconnect()

    def disconnect(self):
        if self._signal_math:
            self._signal_math.remove()
            self._signal_math = None
        if self._name_watch:
            self._name_watch.cancel()
            self._name_watch = None
        self._player = None
        self._player_prop = None
        self.remove_from_connection()
        BasePlayer.disconnect(self)

    def _player_properties_changed(self, iface, changed, invalidated):
        caps_props = ['CanGoNext', 'CanGoPrevious', 'CanPlay', 'CanPause', 'CanSeek']
        status_props = ['PlaybackStatus', 'LoopStatus', 'Shuffle']
        for caps in caps_props:
            if caps in changed:
                self.CapsChange(self._get_caps())
                break
        for status in status_props:
            if status in changed:
                self.StatusChange(self._get_status())
        if 'Metadata' in changed:
            self.TrackChange(self._get_metadata())

    @property
    def object_path(self):
        return self._object_path
            
    @property
    def connected(self):
        return self._connected

    def next(self):
        self._player.Next()

    def prev(self):
        self._player.Previous()

    def pause(self):
        self._player.Pause()

    def stop(self):
        self._player.Stop()
    
    def play(self):
        self._player.Play()
    
    def set_repeat(self, repeat):
        try:
            if repeat == REPEAT_TRACK:
                self._player_prop.Set(MPRIS2_IFACE, 'LoopStatus', 'Track')
            elif repeat == REPEAT_ALL:
                self._player_prop.Set(MPRIS2_IFACE, 'LoopStatus', 'Playlist')
            else:
                self._player_prop.Set(MPRIS2_IFACE, 'LoopStatus', 'None')
        except:
            pass

    def get_status(self):
        playback_dict = {'Playing': STATUS_PLAYING,
                         'Paused': STATUS_PAUSED,
                         'Stopped': STATUS_STOPPED}
        try:
            return status_dict[self._player_prop.Get(MPRIS2_IFACE, 'PlaybackStatus')]
        except:
            return STATUS_PLAYING

    def get_repeat(self):
        repeat_dict = {'None': REPEAT_NONE,
                       'Track': REPEAT_TRACK,
                       'Playlist': REPEAT_ALL}
        try:
            return repeat_dict[self._player_prop.Get(MPRIS2_IFACE, 'LoopStatus')]
        except:
            return REPEAT_NONE

    def get_shuffle(self):
        try:
            return True if self._player_prop.Get(MPRIS2_IFACE, 'Shuffle') else False
        except:
            return False

    def get_metadata(self):
        metadata = self._player_prop.Get(MPRIS2_IFACE, 'Metadata')
        return Metadata.from_mpris2(metadata)

    def get_caps(self):
        caps = set()
        caps_dict = { 'CanGoNext': CAPS_NEXT,
                      'CanGoPrevious': CAPS_PREV,
                      'CanPlay': CAPS_PLAY,
                      'CanPause': CAPS_PAUSE,
                      'CanSeek': CAPS_SEEK,
            }
        for k, v in caps_dict.items():
            if self._player_prop.Get(MPRIS2_IFACE, k):
                caps.add(v)
        return caps

    def set_volume(self, volume):
        self._player_prop.Set(MPRIS2_IFACE, 'Volume', volume)
    
    def get_volume(self):
        return self._player_prop.Get(MPRIS2_IFACE, 'Volume')
    
    def set_position(self, time_in_mili):
        track_id = self._player_prop.Get(MPRIS2_IFACE, 'Metadata')['mpris:trackid']
        self._player.SetPosition(track_id, time_in_mili * 1000)
    
    def get_position(self):
        return self._player_prop.Get(MPRIS2_IFACE, 'Position') / 1000

def run():
    mpris2 = ProxyObject()
    mpris2.run()

if __name__ == '__main__':
    run()
