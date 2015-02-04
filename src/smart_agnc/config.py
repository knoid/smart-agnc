# -*- coding: utf-8 -*-

"""this file is intended to handle the configuration files and data"""

# system imports
import base64
import ConfigParser
import logging
import os
import re

# local imports
from . import config_file

non_printables = ''.join([unichr(x) for x in (range(0, 32) + range(127, 160))])
non_printables_re = re.compile('[%s]' % re.escape(non_printables))
logger = logging.getLogger(__name__)


class UserPreferences(object):
    """
    This is just an even safer implementation of the SafeConfigParser that
    tries to read and write without throwing exceptions.
    """

    _modification_time = -1
    scp = None

    def __init__(self, defaults, vpn):
        self.defaults = defaults
        self.vpn = vpn
        self._read_config()

    def _read_config(self):
        try:
            new_modification_time = os.path.getmtime(config_file)
        except os.error:
            new_modification_time = 0  # force ConfigParser setup

        if new_modification_time > self._modification_time:
            self._modification_time = new_modification_time

            self.scp = ConfigParser.SafeConfigParser()
            self.scp.read(config_file)

    def write_to_disk(self):
        with open(config_file, 'wb') as fileh:
            self.scp.write(fileh)

    def get_connection_values(self):
        section_keys = (('vpn', ['account', 'username', 'password']),
                        ('proxy', ['server', 'user', 'password']))
        user_info = None
        res = []

        for section, keys in section_keys:
            values = {}
            for key in keys:
                values[key] = self.get(section, key)

            if len(values['password']) > 0:
                try:
                    decoded_password = base64.b64decode(values['password'])
                except TypeError:
                    decoded_password = ''
                if len(decoded_password) > 0 and is_printable(decoded_password):
                    # password was base64 encoded
                    values['password'] = decoded_password
                else:
                    logger.warning('Password was not encoded in config file.')

            if len(values) == 0:
                if not user_info:
                    user_info = self.vpn.get_user_info()
                for key in keys:
                    agnc_key = 'Proxy' * (section == 'proxy') + key.title()
                    values[key] = user_info[agnc_key]

            res.append(filter_empty(values))

        return res

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


def is_printable(string):
    return non_printables_re.search(string) is None


def filter_empty(values):
    return dict((key, val) for key, val in values.items() if len(val) > 0)
