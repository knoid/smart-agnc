"""this file is intended to handle the configuration files and data"""

import os
import ConfigParser
import atexit

SECTION = 'DEFAULT'

class UserPreferences(object):
    """UserPreferences"""

    written = True

    def __init__(self, defaults=None, filepath=''):
        if filepath == '':
            filepath = os.path.expanduser('~/.smart-agnc')

        self.rcp = ConfigParser.SafeConfigParser(defaults)
        try:
            self.rcp.read(filepath)
        except ConfigParser.ParsingError:
            pass

        atexit.register(self.__check_write_to_disk__, filepath)

    def write_to_disk(self, filepath):
        """Call it at the end, this function won't save it twice"""
        with open(filepath, 'wb') as fileh:
            self.rcp.write(fileh)
        self.written = True

    def __check_write_to_disk__(self, filepath):
        """_check_write_to_disk"""
        if not self.written:
            self.write_to_disk(filepath)

    def set(self, key, value):
        """set"""
        self.rcp.set(SECTION, key, value)
        self.written = False
        return value

    def setboolean(self, key, value):
        """setboolean"""
        return self.set(key, 'on' if value else 'off')

    def get(self, key):
        """get"""
        try:
            return self.rcp.get(SECTION, key)
        except ConfigParser.NoOptionError:
            return ''

    def getboolean(self, key):
        """getboolean"""
        try:
            return self.rcp.getboolean(SECTION, key)
        except ConfigParser.NoOptionError:
            return False
