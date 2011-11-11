#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import GLib


CONFIG_FILE = os.path.join(
        GLib.get_user_config_dir(),
        'remember-the-rhythm.last'
        )

class RememberTheRhythm(GObject.Object, Peas.Activatable):

    __gtype_name = 'RememberTheRhythm'

    object = GObject.property(type=GObject.Object)
    location = None
    playback_time = 0
    first_run = False

    def __init__(self):
        GObject.Object.__init__(self)
        try:
            config_file = open(CONFIG_FILE, 'r')
            config_data = config_file.read()
            config_file.close()
        except IOError:
            return

        config_data = config_data.split()
        if config_data:
            self.location = config_data[0]
            self.playback_time = long(config_data[1])

    def do_activate(self):
        self.shell = self.object
        self.shell_player = self.shell.props.shell_player
        self.db = self.shell.props.db
        self.shell_player.connect('elapsed-changed', self.elapsed_changed)
        self.shell_player.connect('playing-song-changed', self.playing_changed)
        self.shell.connect('database-load-complete', self.load_complete)

    def do_deactivate(self):
        self.save_rhythm()

    def load_complete(self, *args, **kwargs):
        if self.location:
            entry = self.db.entry_lookup_by_location(self.location)
            source = self.shell.guess_source_for_uri(self.location)
            self.shell_player.set_mute(True)
            self.shell_player.play_entry(entry, source)
            self.first_run = True

    def playing_changed(self, player, entry, data=None):
        if self.first_run:
            self.shell_player.set_playing_time(long(self.playback_time))
            self.shell_player.set_mute(False)
            self.first_run = False
            return

        try:
            self.location = entry.get_string(RB.RhythmDBPropType.LOCATION)
            #if not new_location == self.location:
            #    GObject.idle_add(self.save_rhythm, '0')
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
            config_file = open(CONFIG_FILE, 'w')
            config_data = '\n'.join([self.location, str(pb_time)])
            config_file.write(config_data)
            config_file.close()
