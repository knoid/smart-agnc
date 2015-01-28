# -*- coding: utf-8 -*-

# system imports
import base64
import gobject
import gtk
import os
import re

from windows import _WindowForm


class NewPasswordWindow(_WindowForm):

    def __init__(self):
        super(NewPasswordWindow, self).__init__()

        self.set_title(_('Smart AGNC: Set new password'))

        self._make_label(_('New password:'), 0, 0)
        self.txt_password1 = self._make_entry(1, 0)
        self.txt_password1.set_visibility(False)

        self._make_label(_('Repeat password:'), 0, 1)
        self.txt_password2 = self._make_entry(1, 1)
        self.txt_password2.set_visibility(False)

        close_save = gtk.Button(stock=gtk.STOCK_SAVE)
        self._attach(close_save, 1, 3)
        close_save.connect('clicked', self.__on_submit__)

        self.table.show_all()
        self.connect('form_submit', self.__on_submit__)

    def present(self):
        self.txt_password1.set_text('')
        self.txt_password2.set_text('')
        super(NewPasswordWindow, self).present()

    def request_new_password(self):
        new_password = random_string()

        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL,
            _('The password `%s` has been generated for you. Would you like ' +
              'to use it? Be sure to copy it first.') % new_password)
        dialog.set_title(_('Smart AGNC: Time for a new password'))

        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_OK:
            self.emit('new-password', new_password)
        else:
            self.set_position(gtk.WIN_POS_CENTER)
            self.set_transient_for(None)
            self.present()

    def __on_submit__(self, widget):
        password1 = self.txt_password1.get_text()
        password2 = self.txt_password2.get_text()
        if password1 == password2 and is_valid_password(password1):
            self.emit('new-password', password1)
            self.hide()
        else:
            if password1 == password2:
                d_text = _('Password must contain numbers, uppercase and ' +
                           'lowercase letters.')
            else:
                d_text = _('Passwords don\'t match.')
            dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK,
                                       d_text)
            dialog.set_title(_('Error'))
            dialog.run()
            dialog.destroy()

gobject.signal_new('new-password', NewPasswordWindow,
                   gobject.SIGNAL_RUN_CLEANUP, None, (str, ))


def random_string(length=8):
    r_string = ''
    while not is_valid_password(r_string):
        r_string = base64.urlsafe_b64encode(os.urandom(length))[:length]
    return r_string

test_number = re.compile('[0-9]')


def is_valid_password(password):
    return len(password) > 7 and password != password.lower() \
        and test_number.search(password)
