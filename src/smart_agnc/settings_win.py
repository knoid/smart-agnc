# -*- coding: utf-8 -*-

"""settings_win.py"""

# system imports
import gobject
import gtk

from _window_form import _WindowForm
import agn_binder as ab


class ConfigurationWindow(_WindowForm):
    """ConfigurationWindow"""

    def __init__(self, vpn, values, change_password_win):
        super(ConfigurationWindow, self).__init__()

        self.set_resizable(False)
        self.set_title(_('Configuration'))

        self._make_label(_('Account'), 0, 0)
        self.txt_account = self._make_entry(1, 0)

        self._make_label(_('Username'), 0, 1)
        self.txt_username = self._make_entry(1, 1)

        self._make_label(_('Password'), 0, 2)
        self.txt_password = self._make_entry(1, 2)
        self.txt_password.set_visibility(False)

        check_button = gtk.CheckButton(_('Show password'))
        self._attach(check_button, 2, 2)
        check_button.connect('toggled', self.on_password_visiblity)

        close_save = gtk.Button(stock=gtk.STOCK_SAVE)
        close_save.set_flags(gtk.CAN_DEFAULT)
        close_save.connect('clicked', self.do_btn_save)
        self._attach(close_save, 1, 3)

        self.change_password = button = gtk.Button(_('Change Password'))
        button.set_tooltip_text(_('You should disconnect first'))
        button.connect('clicked', present_window(change_password_win))
        self._attach(button, 2, 3)

        self.table.show_all()
        self.connect('form_submit', self.__on_submit__)

        vpn.connect('agn_state_change', self.on_agn_state_change)
        self.on_agn_state_change(vpn, vpn.get_state())

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
        self.emit('save',
                  self.txt_account.get_text(),
                  self.txt_username.get_text(),
                  self.txt_password.get_text())

    def on_agn_state_change(self, vpn, state):
        enabled = state < ab.STATE_BEFORE_CONNECT
        self.change_password.set_sensitive(enabled)
        self.change_password.set_has_tooltip(not enabled)

    def on_password_visiblity(self, widget):
        """on_password_visiblity"""
        self.txt_password.set_visibility(widget.get_active())

    def __on_submit__(self, _):
        self.do_btn_save(False)


def present_window(win):
    return lambda w: win.present()

gobject.signal_new('save', ConfigurationWindow, gobject.SIGNAL_RUN_FIRST,
                   None, (str, str, str, ))
