# -*- coding: utf-8 -*-

"""this file is intended to handle the configuration files and data"""

import os
import ConfigParser

class UserPreferences(object):
    """
    This is just an even safer implementation of the SafeConfigParser that tries
    to read and write without throwing exceptions.
    """

    _modification_time = -1
    scp = None

    def __init__(self, defaults=None, filepath='~/.smart-agnc'):
        self.defaults = defaults if defaults else {}
        self.filepath = os.path.expanduser(filepath)

        self._read_config()

    def _read_config(self):
        try:
            new_modification_time = os.path.getmtime(self.filepath)
        except os.error:
            new_modification_time = 0 # force ConfigParser setup

        if new_modification_time > self._modification_time:
            self._modification_time = new_modification_time

            self.scp = ConfigParser.SafeConfigParser()
            self.scp.read(self.filepath)

    def write_to_disk(self):
        with open(self.filepath, 'wb') as fileh:
            self.scp.write(fileh)

    def set(self, section, key, value):
        self._read_config()
        try:
            return self.scp.set(section, key, value)
        except ConfigParser.NoSectionError:
            self.scp.add_section(section)
            self.set(section, key, value)

    def setboolean(self, section, key, value):
        return self.set(section, key, 'on' if value else 'off')

    def get(self, section, key, default=''):
        try:
            return self.scp.get(section, key)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            if key in self.defaults:
                return self.defaults[key]
            else:
                return default

    def getboolean(self, section, key):
        try:
            return self.scp.getboolean(section, key)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return self.get(section, key, False)

    def getint(self, section, key):
        try:
            return self.scp.getint(section, key)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return self.get(section, key, 0)
