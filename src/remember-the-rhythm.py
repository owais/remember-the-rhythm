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
KEY_PLAYLIST = 'playlist'
KEY_BROWSER_VALUES = 'browser-values'


class RememberTheRhythm(GObject.Object, Peas.Activatable):

    __gtype_name = 'RememberTheRhythm'
    object = GObject.property(type=GObject.Object)

    first_run = False

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new(GSETTINGS_KEY)
        self.location = self.settings.get_string(KEY_LOCATION)
        self.playlist = self.settings.get_string(KEY_PLAYLIST)
        self.playback_time = self.settings.get_uint(KEY_PLAYBACK_TIME)
        self.browser_values_list = self.settings.get_value(KEY_BROWSER_VALUES)
        self.source = None

    def do_activate(self):
        self.shell = self.object
        self.library = self.shell.props.library_source
        self.shell_player = self.shell.props.shell_player
        self.playlist_manager = self.shell.props.playlist_manager
        self.db = self.shell.props.db
        self.backend_player = self.shell_player.props.player
        self.shell_player.connect('playing-changed', self.playing_changed)
        self.shell_player.connect('playing-source-changed', self.playing_source_changed)
        self.shell.props.db.connect('load-complete', self.load_complete)
        self.shell_player.connect('elapsed-changed', self.elapsed_changed)

    def do_deactivate(self):
        self.save_rhythm()

    def load_complete(self, *args, **kwargs):
        if self.location:
            entry = self.db.entry_lookup_by_location(self.location)
            if self.playlist:
                playlists = self.playlist_manager.get_playlists()
                for playlist in playlists:
                    if playlist.props.name == self.playlist:
                        self.source = playlist
                        break
            if not self.source:
                self.source = self.shell.guess_source_for_uri(self.location)
            self.shell_player.set_playing_source(self.source)
            self.shell_player.set_selected_source(self.source)
            self.shell_player.play_entry(entry, self.source)
            self.first_run = True

    def playing_source_changed(self, player, source, data=None):
        if source:
            self.source = source
            if self.source in self.playlist_manager.get_playlists():
                self.settings.set_string('playlist', self.source.props.name)
            else:
                self.settings.set_string('playlist', '')

    def playing_changed(self, player, playing, data=None):
        if self.first_run:
            self.first_run = False
            try:
                self.shell_player.set_playing_time(self.playback_time)
            except:
                pass
            GObject.idle_add(self.init_source)
            return

        try:
            entry = self.shell_player.get_playing_entry()
            self.location = entry.get_string(RB.RhythmDBPropType.LOCATION)
            GObject.idle_add(self.save_rhythm, 0)
        except:
            return


    def elapsed_changed(self, player, entry, data=None):
        try:
            self.playback_time = self.shell_player.get_playing_time()[1]
        except:
            pass

    def get_source_data(self):
        if self.source:
            views = self.source.get_property_views()
            browser_values_list = []
            for view in views:
                browser_values_list.append(view.get_selection())
            self.browser_values_list = Variant('aas', browser_values_list)
            self.settings.set_value(KEY_BROWSER_VALUES, self.browser_values_list)

    def init_source(self):
        if self.source:
            views = self.source.get_property_views()
            for i, view in enumerate(views):
                value = self.browser_values_list[i]
                if value:
                    view.set_selection(value)
            self.shell.props.display_page_tree.select(self.source)
            self.shell_player.jump_to_current()

    def save_rhythm(self, pb_time=None):
        if self.location:
            pb_time = pb_time == None and self.playback_time or pb_time
            self.settings.set_uint(KEY_PLAYBACK_TIME, pb_time)
            self.settings.set_string(KEY_LOCATION, self.location)
        GObject.idle_add(self.get_source_data)


