#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import GLib


CONFIG_FILE = os.path.join(GLib.get_user_config_dir(), 'remember-the-rhythm.last')

class RememberTheRhythm(GObject.Object, Peas.Activatable):
    __gtype_name = 'RememberTheRhythm'
    object = GObject.property(type=GObject.Object)
    location = None
    playback_time = None

    def __init__(self):
        GObject.Object.__init__(self)
        try:
            config_data = open(CONFIG_FILE, 'r').read()
        except IOError:
            return
        config_data = config_data.split()
        if config_data:
            self.location, self.playback_time = config_data

    def do_activate(self):
        self.shell = self.object
        self.shell_player = self.shell.props.shell_player
        self.db = self.shell.props.db
        self.shell.connect('database-load-complete', self.load_complete)
        self.shell_player.connect('elapsed-changed', self.elapsed_changed)
        self.shell_player.connect('playing-song-changed', self.playing_changed)

    def do_deactivate(self):
        self.save_rhythm()

    def load_complete(self, *args, **kwargs):
        if self.location:
            entry = self.db.entry_lookup_by_location(self.location)
            source = self.shell.guess_source_for_uri(self.location)
            self.shell_player.play_entry(entry, source)
            if self.playback_time:
                self.shell_player.set_playing_time(long(self.playback_time))

    def save_rhythm(self):
        config_file = open(CONFIG_FILE, 'w')
        config_data = '\n'.join([self.location, self.playback_time])
        config_file.write(config_data)
        config_file.close()

    def playing_changed(self, player, entry, data=None):
        try:
            self.location = str(entry.get_string(RB.RhythmDBPropType.LOCATION))
            self.save_rhythm()
        except:
            pass

    def elapsed_changed(self, player, entry, data=None):
        try:
            self.playback_time = str(self.shell_player.get_playing_time()[1])
        except:
            pass
