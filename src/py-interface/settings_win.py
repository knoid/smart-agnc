"""settings_win.py"""

# system imports
import gobject
import gtk

from _window import _Window

class ConfigurationWindow(_Window):
    """ConfigurationWindow"""

    def __init__(self, values=False):
        super(ConfigurationWindow, self).__init__()

        self.set_resizable(False)
        self.set_size_request(400, 200)
        self.set_title('Configuration')

        self.table = table = gtk.Table(rows=4, columns=3)
        table.set_col_spacings(10)
        table.set_row_spacings(10)

        self.__make_label__('Account', 0, 0)
        self.txt_account = self.__make_entry__(1, 0)

        self.__make_label__('Username', 0, 1)
        self.txt_username = self.__make_entry__(1, 1)

        self.__make_label__('Password', 0, 2)
        self.txt_password = self.__make_entry__(1, 2)
        self.txt_password.set_visibility(False)

        check_button = gtk.CheckButton('Show password')
        self._attach(check_button, 2, 2)
        check_button.connect('toggled', self.on_password_visiblity)

        close_save = gtk.Button(stock=gtk.STOCK_SAVE)
        close_save.set_flags(gtk.CAN_DEFAULT)
        close_save.connect('clicked', self.do_btn_save)
        self._attach(close_save, 1, 3)

        self.add(table)
        table.show_all()
        self.connect('form_submit', self.__on_submit__)
        if values:
            self.set_values(values)

    def set_values(self, values):
        """set_values"""
        value_mapper = {
            'account':  self.txt_account,
            'username': self.txt_username,
            'password': self.txt_password
        }
        for key, entry in value_mapper.iteritems():
            if key in values:
                entry.set_text(values[key])

    def _attach(self, widget, left, top):
        """_attach"""
        self.table.attach(widget, left, left + 1, top, top + 1, 0, 0, 0, 0)

    def __make_entry__(self, left, top):
        entry = gtk.Entry()
        entry.set_max_length(80)
        entry.set_width_chars(20)
        self._attach(entry, left, top)
        return entry

    def __make_label__(self, txt, left, top):
        label = gtk.Label(txt)
        self._attach(label, left, top)

    def do_btn_save(self, _):
        """do_btn_save"""
        self.emit('save', self.txt_account.get_text(),
                          self.txt_username.get_text(),
                          self.txt_password.get_text())

    def on_password_visiblity(self, widget):
        """on_password_visiblity"""
        self.txt_password.set_visibility(widget.get_active())

    def __on_submit__(self, _):
        self.do_btn_save(False)

gobject.signal_new('save', ConfigurationWindow, gobject.SIGNAL_RUN_FIRST,
    None, (str, str, str, ))
