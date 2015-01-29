# -*- coding: utf-8 -*-

import gtk
import pango
import webbrowser

from . import __author__, __version__
from windows import _Window, _WindowCentered

_title_ = __package__.replace('_', '-')

tap_url = 'https://tap.innovate.ibm.com/app/3768'
tap_url = '<a href="%s">%s</a>' % (tap_url, tap_url)

readme_url = 'https://github.com/knoid/%s/blob/v%s/README.md' % \
    (_title_, __version__)


class AboutWindow(_WindowCentered, _Window):

    def __init__(self):
        super(AboutWindow, self).__init__()

        self.set_title(_('About Smart AGNC'))

        self.vbox = vbox = gtk.VBox(False, 10)
        self.add(vbox)

        vbox.add(gtk.image_new_from_icon_name(_title_, gtk.ICON_SIZE_DIALOG))
        vbox.add(gtk.Label('Smart AT&T Global Network Client'))

        label = gtk.Label()
        label.set_markup(_('Please go to %s\nand click on Like if you\'ve ' +
                           'found this app to be useful.') % tap_url)
        label.set_justify(gtk.JUSTIFY_CENTER)
        vbox.add(label)

        self.add_attr(_('Author'), __author__)
        self.add_attr(_('Version'), __version__)

        hbox = gtk.HBox(True, 100)
        vbox.add(hbox)

        btn_help = gtk.Button(_('Help'))
        btn_help.connect('clicked', lambda b: webbrowser.open(readme_url))
        hbox.add(btn_help)

        btn_close = gtk.Button(_('Close'))
        btn_close.connect('clicked', lambda b: self.hide())
        hbox.add(btn_close)

        vbox.show_all()

    def add_attr(self, label, value):
        hbox = gtk.HBox(True, 10)
        self.vbox.add(hbox)

        lbl_key = gtk.Label(label)
        lbl_key.set_alignment(1, 0.5)
        lbl_key.modify_font(pango.FontDescription('bold'))
        hbox.add(lbl_key)

        lbl_value = gtk.Label(value)
        lbl_value.set_alignment(0, 0.5)
        hbox.add(lbl_value)
