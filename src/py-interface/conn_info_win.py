"""conn_info_win.py"""

# system imports
import gobject
import gtk

from _window import _Window

class ConnectionInformationWindow(_Window):
    """ConnectionInformationWindow"""

    def __init__(self):
        super(ConnectionInformationWindow, self).__init__()

        self.set_size_request(400, 400)
        self.set_title('Connection Information')

        self.text_info = text_info = gtk.TextView()
        text_info.set_editable(False)
        text_info.show()
        self.add(text_info)

    def set_text(self, value):
        """set_text"""
        self.text_info.get_buffer().set_text(value)
