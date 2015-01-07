"""settings_win.py"""

# system imports
import gobject
import gtk

from _window_form import _WindowForm

class ConfigurationWindow(_WindowForm):
    """ConfigurationWindow"""

    def __init__(self, values=False):
        super(ConfigurationWindow, self).__init__()

        self.set_resizable(False)
        self.set_title('Configuration')

        self._make_label('Account', 0, 0)
        self.txt_account = self._make_entry(1, 0)

        self._make_label('Username', 0, 1)
        self.txt_username = self._make_entry(1, 1)

        self._make_label('Password', 0, 2)
        self.txt_password = self._make_entry(1, 2)
        self.txt_password.set_visibility(False)

        check_button = gtk.CheckButton('Show password')
        self._attach(check_button, 2, 2)
        check_button.connect('toggled', self.on_password_visiblity)

        close_save = gtk.Button(stock=gtk.STOCK_SAVE)
        close_save.set_flags(gtk.CAN_DEFAULT)
        close_save.connect('clicked', self.do_btn_save)
        self._attach(close_save, 1, 3)

        self.table.show_all()
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
