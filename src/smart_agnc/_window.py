# -*- coding: utf-8 -*-

# system imports
import gobject
import gtk


class _Window(gtk.Window):
    """
    Abstract Window class that predefines the behaviour of every window. It
    lets you close with Esc and submit with Return. It also adds a new signal
    called `form_submit` to handle the Return key.
    """

    def __init__(self):
        super(_Window, self).__init__()

        self.set_border_width(10)
        self.connect('delete_event', __prevent_destroy__)
        self.connect('key-press-event', __on_key__)


def __on_key__(widget, evt):
    if evt.keyval == gtk.keysyms.Escape:
        widget.hide()

    if evt.keyval == gtk.keysyms.Return:
        widget.emit('form_submit')


def __prevent_destroy__(widget, _=None):
    widget.hide()
    return True

gobject.signal_new('form_submit', _Window, gobject.SIGNAL_RUN_FIRST, None, ())
