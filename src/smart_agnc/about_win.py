# -*- coding: utf-8 -*-

import gtk
import pango

from . import __author__, __version__
from _window_form import _WindowForm

tap_url = 'https://tap.innovate.ibm.com/app/3768'
tap_url = '<a href="%s">%s</a>' % (tap_url, tap_url)


class AboutWindow(_WindowForm):

    def __init__(self):
        super(AboutWindow, self).__init__()

        self.set_title(_('About Smart AGNC'))
        self.table.set_property('n-columns', 2)

        logo = gtk.image_new_from_icon_name('smart-agnc', gtk.ICON_SIZE_DIALOG)
        self._attach(logo, 0, 1, 2)

        label = gtk.Label('Smart AT&T Global Network Client')
        self._attach(label, 0, 2, 2)

        label = gtk.Label()
        label.set_markup(_('Please go to %s\nand click on Like if you\'ve ' +
                           'found this app to be useful.') % tap_url)
        label.set_justify(gtk.JUSTIFY_CENTER)
        self._attach(label, 0, 3, 2)

        self.add_attr(_('Author'), __author__, 4)
        self.add_attr(_('Version'), __version__, 5)

        self.table.show_all()

    def add_attr(self, label, value, top):
        key = self._make_label(label, 0, top)
        key.set_alignment(1, 0.5)
        key.modify_font(pango.FontDescription("bold"))

        self._make_label(value, 1, top)

if __name__ == '__main__':
    import gettext
    gettext.install('smart-agnc')

    a = About()
    a.present()

    gtk.main()
