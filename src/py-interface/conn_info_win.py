"""conn_info_win.py"""

# system imports
import gobject
import gtk

class ConnectionInformationWindow(gtk.Window):
    """ConnectionInformationWindow"""

    def __init__(self):
        super(ConnectionInformationWindow, self).__init__()

        self.set_border_width(10)
        self.set_size_request(400, 400)
        self.set_title('Connection Information')

        self.text_info = text_info = gtk.TextView()
        text_info.set_editable(False)
        text_info.show()
        self.add(text_info)

        self.connect('delete_event', __prevent_destroy__)

    def set_text(self, value):
        """set_text"""
        self.text_info.get_buffer().set_text(value)

def __prevent_destroy__(widget, _=None):
    widget.hide()
    return True
