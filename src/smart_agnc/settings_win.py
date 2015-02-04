# -*- coding: utf-8 -*-

# system imports
import gobject
import gtk

from windows import _WindowCentered, _WindowForm
import agn_binder as ab


class ConfigurationWindow(_WindowCentered, _WindowForm):

    txt_account = None
    txt_username = None
    txt_password = None

    txt_proxy_server = None
    txt_proxy_user = None
    txt_proxy_password = None

    def __init__(self, events, vpn, use_proxy, proxy, change_password_win):
        super(ConfigurationWindow, self).__init__()

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
        check_button.connect('toggled', self.on_password_visiblity,
                             self.txt_password)

        self.check_proxy = gtk.CheckButton(_('Enable proxy settings'))
        self.check_proxy.set_active(use_proxy)
        self.check_proxy.set_alignment(0, 0.5)
        self._attach(self.check_proxy, 1, 3, 2)
        self.check_proxy.connect('toggled', self.on_proxy_toggled)

        self.close_save = close_save = gtk.Button(stock=gtk.STOCK_SAVE)
        close_save.set_flags(gtk.CAN_DEFAULT)
        close_save.connect('clicked', self.do_btn_save)
        self._attach(close_save, 1, 5)

        self.change_password = button = gtk.Button(_('Change Password'))
        button.set_tooltip_text(_('You should disconnect first'))
        button.connect('clicked', self.do_change_password, change_password_win)
        self._attach(button, 2, 5)

        self.table.show_all()
        self.connect('form-submit', self.__on_submit__)
        self.connect('hide', self.__on_hide__, change_password_win)

        self.proxy_table = self.init_proxy_table()
        self._attach(self.proxy_table, 0, 4, 3)

        events.connect('agn-state-change', self.on_agn_state_change)
        self.on_proxy_toggled(self.check_proxy)

        self.vpn_mapper = {
            'account':  self.txt_account,
            'username': self.txt_username,
            'password': self.txt_password
        }
        self.proxy_mapper = {
            'server': self.txt_proxy_server,
            'user': self.txt_proxy_user,
            'password': self.txt_proxy_password
        }

        self.set_values(vpn, use_proxy, proxy)

    def init_proxy_table(self):
        table = gtk.Table()
        table.set_col_spacings(10)
        table.set_row_spacings(10)
        self._make_label(_('Server'), 0, 0, table)
        self.txt_proxy_server = self._make_entry(1, 0, table)

        self._make_label(_('User'), 0, 1, table)
        self.txt_proxy_user = self._make_entry(1, 1, table)

        self._make_label(_('Password'), 0, 2, table)
        self.txt_proxy_password = self._make_entry(1, 2, table)
        self.txt_proxy_password.set_visibility(False)

        check_button = gtk.CheckButton(_('Show password'))
        self._attach(check_button, 2, 2, table=table)
        check_button.connect('toggled', self.on_password_visiblity,
                             self.txt_proxy_password)

        table.show_all()
        return table

    def set_values(self, vpn, use_proxy, proxy):
        for mapper, values in ((self.vpn_mapper, vpn),
                               (self.proxy_mapper, proxy)):
            for key, entry in mapper.iteritems():
                if key in values:
                    entry.set_text(values[key])

        self.check_proxy.set_active(use_proxy)
        self.on_proxy_toggled(self.check_proxy)

    def do_btn_save(self, unused):
        ret = {}
        mappers = [('vpn', self.vpn_mapper), ('proxy', self.proxy_mapper)]
        for sect, mapper in mappers:
            items = mapper.iteritems()
            ret[sect] = (dict([(key, txt.get_text()) for key, txt in items]))
        self.emit('save',
                  ret['vpn']['account'],
                  ret['vpn']['username'],
                  ret['vpn']['password'],
                  self.check_proxy.get_active(),
                  ret['proxy']['server'],
                  ret['proxy']['user'],
                  ret['proxy']['password'])

    def do_change_password(self, unused_btn, change_password_win):
        change_password_win.set_position(gtk.WIN_POS_NONE)
        change_password_win.set_transient_for(self)
        change_password_win.present()

    def on_agn_state_change(self, unused_vpn, state):
        enabled = state < ab.STATE_BEFORE_CONNECT
        self.change_password.set_sensitive(enabled)
        self.change_password.set_has_tooltip(not enabled)

    def on_password_visiblity(self, widget, password_field):
        password_field.set_visibility(widget.get_active())

    def on_proxy_toggled(self, widget):
        if widget.get_active():
            self.proxy_table.show()
        else:
            self.proxy_table.hide()

    def __on_hide__(self, unused, change_password_win):
        if change_password_win.get_transient_for() is self:
            change_password_win.hide()

    def __on_submit__(self, unused):
        self.do_btn_save(False)


gobject.signal_new('save', ConfigurationWindow, gobject.SIGNAL_RUN_FIRST,
                   None, (str, str, str, bool, str, str, str, ))
