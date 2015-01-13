# -*- coding: utf-8 -*-

"""conn_info_win.py"""

# system imports
import gtk
import time

from _window import _Window
from agn_binder import long2ip


class ConnectionInformationWindow(_Window):
    """ConnectionInformationWindow"""

    def __init__(self):
        super(ConnectionInformationWindow, self).__init__()

        self.set_size_request(400, 400)
        self.set_title(_('Connection Information'))

        self.text_info = text_info = gtk.TextView()
        text_info.set_editable(False)
        text_info.show()
        self.add(text_info)

    def set_dict(self, data):
        text = []
        for key, value in data.iteritems():
            if 'IP' in key:
                value = long2ip(int(value))
            if 'Bytes' in key:
                value = bytes2human(int(value))
            if 'Time' in key:
                value = int(value)
                value = time.ctime(value) if value > 0 else 'None'
            text.append('%s: %s' % (key, value))
        self.set_text('\n'.join(sorted(text)))

    def set_text(self, text):
        """set_text"""
        self.text_info.get_buffer().set_text(text)


def bytes2human(num, format_str='%3.1f %sB'):
    """http://stackoverflow.com/questions/1094841"""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return format_str % (num, unit)
        num /= 1024.0
    return format_str % (num, 'Yi')
