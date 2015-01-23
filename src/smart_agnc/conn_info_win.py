# -*- coding: utf-8 -*-

# system imports
import time

from _window_form import _WindowForm
from agn_binder import long2ip


class ConnectionInformationWindow(_WindowForm):

    fields = {}

    def __init__(self):
        super(ConnectionInformationWindow, self).__init__()

        self.set_title(_('Connection Information'))
        self.table.set_property('n-columns', 2)
        self.table.show_all()

    def set_dict(self, data):
        for key, value in sorted(data.iteritems()):
            if 'IP' in key:
                label = long2ip(value) if value else _('Not available.')
            elif 'Bytes' in key:
                label = bytes2human(value)
            elif 'Time' in key:
                label = time.ctime(value) if value else _('Not available.')
            elif 'Active' in key:
                label = _('Yes.') if value else _('No.')
            else:
                label = str(value)

            if key not in self.fields:
                self._make_label(_(key), 0, len(self.fields)).show()
                txt = self._make_label('', 1, len(self.fields))
                txt.set_selectable(True)
                txt.show()
                self.fields[key] = txt
            self.fields[key].set_label(label)


def bytes2human(num, format_str='%3.1f %sB'):
    """http://stackoverflow.com/questions/1094841"""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return format_str % (num, unit)
        num /= 1024.0
    return format_str % (num, 'Yi')


def gettext_keys(_):
    """This is here so this keywords appear on the language files editor."""
    _('BytesReceivedAtStartOfConnection')
    _('BytesSentAtStartOfConnection')
    _('ConnectType')
    _('InternetIPAddress')
    _('InternetGatewayIPAddress')
    _('InternetAdapter')
    _('InternetMACAddress')
    _('StatusCode')
    _('StatusText')
    _('TimeCompleted')
    _('TimeConnected')
    _('TimeStarted')
    _('VPNCompressionActive')
    _('VPNIPAddress')
    _('VPNServerIPAddress')
    _('VPNTunnelAdapter')
