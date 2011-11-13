#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import Gio


GSETTINGS_KEY = "org.gnome.rhythmbox.plugins.remember-the-rhythm"
KEY_PLAYBACK_TIME = 'playback-time'
KEY_LOCATION = 'last-entry-location'


class RememberTheRhythm(GObject.Object, Peas.Activatable):

    __gtype_name = 'RememberTheRhythm'
    object = GObject.property(type=GObject.Object)

    first_run = False

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new(GSETTINGS_KEY)
        self.location = self.settings.get_string(KEY_LOCATION)
        self.playback_time = self.settings.get_uint(KEY_PLAYBACK_TIME)

    def do_activate(self):
        self.shell = self.object
        self.shell_player = self.shell.props.shell_player
        self.db = self.shell.props.db
        self.shell_player.connect('playing-song-changed', self.playing_song_changed)
        self.shell.connect('database-load-complete', self.load_complete)
        self.shell_player.connect('elapsed-changed', self.elapsed_changed)

    def do_deactivate(self):
        self.save_rhythm()

    def load_complete(self, *args, **kwargs):
        if self.location:
            entry = self.db.entry_lookup_by_location(self.location)
            source = self.shell.guess_source_for_uri(self.location)
            self.shell_player.set_mute(True)
            self.shell_player.play_entry(entry, source)
            self.first_run = True

    def playing_song_changed(self, player, entry, data=None):
        if self.first_run:
            self.shell_player.set_playing_time(self.playback_time)
            self.shell_player.set_mute(False)
            self.first_run = False
            return

        try:
            self.location = entry.get_string(RB.RhythmDBPropType.LOCATION)
        except:
            return

        GObject.idle_add(self.save_rhythm, 0)

    def elapsed_changed(self, player, entry, data=None):
        try:
            self.playback_time = self.shell_player.get_playing_time()[1]
        except:
            pass

    def save_rhythm(self, pb_time=None):
        if self.location:
            pb_time = pb_time == None and self.playback_time or pb_time
            self.settings.set_uint(KEY_PLAYBACK_TIME, pb_time)
            self.settings.set_string(KEY_LOCATION, self.location)
