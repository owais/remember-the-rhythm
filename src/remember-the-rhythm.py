#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import Gio
from gi.repository.GLib import Variant


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
        self.browser_values_list = self.settings.get_value('browser-values')

    def do_activate(self):
        self.shell = self.object
        self.library = self.shell.props.library_source
        self.shell_player = self.shell.props.shell_player
        self.db = self.shell.props.db
        self.backend_player = self.shell_player.props.player
        self.shell_player.connect('playing-song-changed', self.playing_song_changed)
        self.shell.connect('database-load-complete', self.load_complete)
        self.shell_player.connect('elapsed-changed', self.elapsed_changed)

    def do_deactivate(self):
        self.save_rhythm()

    def load_complete(self, *args, **kwargs):
        if self.location:
            entry = self.db.entry_lookup_by_location(self.location)
            source = self.shell.guess_source_for_uri(self.location)
            self.shell_player.play_entry(entry, source)
            self.first_run = True

        GObject.idle_add(self.set_browser_values)

    def playing_song_changed(self, player, entry, data=None):
        if self.first_run:
            self.first_run = False
            try:
                self.shell_player.set_playing_time(self.playback_time)
            except:
                pass
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

    def get_browser_values(self):
        views = self.library.get_property_views()
        browser_values_list = []
        for view in views:
            browser_values_list.append(view.get_selection())
        self.browser_values_list = Variant('aas', browser_values_list)
        self.settings.set_value('browser-values', self.browser_values_list)

    def set_browser_values(self):
        views = self.library.get_property_views()
        for i, view in enumerate(views):
            value = self.browser_values_list[i]
            view.set_selection(value)

    def save_rhythm(self, pb_time=None):
        if self.location:
            pb_time = pb_time == None and self.playback_time or pb_time
            self.settings.set_uint(KEY_PLAYBACK_TIME, pb_time)
            self.settings.set_string(KEY_LOCATION, self.location)
        self.get_browser_values()


