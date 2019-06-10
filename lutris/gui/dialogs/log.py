"""Window to show game logs"""
import os
from gi.repository import Gtk, Gdk
from lutris.gui.widgets.log_text_view import LogTextView
from lutris.settings import LOG_PATH
from lutris.gui import dialogs
import lutris.util.system as system
from lutris.gui.widgets.utils import open_uri
import datetime

class LogWindow(Gtk.ApplicationWindow):
    def __init__(self, title=None, buffer=None, application=None):
        super().__init__(icon_name="lutris", application=application)
        self.game_title = title
        self.set_title("Log for {}".format(title))
        self.set_show_menubar(False)

        self.set_size_request(640, 480)
        self.buffer = buffer
        self.logtextview = LogTextView(self.buffer)

        self.vbox = Gtk.VBox(spacing=0)
        self.vbox.set_homogeneous(False)
        self.add(self.vbox)

        scrolledwindow = Gtk.ScrolledWindow(
            hexpand=True, vexpand=True, child=self.logtextview
        )
        self.vbox.pack_start(scrolledwindow, True, True, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_entry.props.placeholder_text = "Search..."
        self.search_entry.connect("stop-search", self.dettach_search_entry)
        self.search_entry.connect("search-changed", self.logtextview.find_first)
        self.search_entry.connect("next-match", self.logtextview.find_next)
        self.search_entry.connect("previous-match", self.logtextview.find_previous)

        self.connect("key-press-event", self.on_key_press_event)

        self.hbox = Gtk.HBox()
        self.hbox.set_spacing(0)

        self.hbox.pack_start(self.search_entry, False, True, 10)

        button = Gtk.Button.new_with_label("Clear Log")
        button.connect("clicked", self.clear_log)
        button.set_tooltip_text("Clears log-window")
        self.hbox.pack_end(button, False, False, 10)

        button = Gtk.Button.new_with_label("Save Log")
        button.connect("clicked", self.save_log)
        button.set_tooltip_text("Saves Log-Window")
        self.hbox.pack_end(button, False, False, 0)

        button = Gtk.Button.new_from_icon_name(
            "system-file-manager-symbolic", Gtk.IconSize.MENU
        )
        button.set_tooltip_text("Open Logs-Folder")
        button.set_size_request(32, 32)
        button.connect("clicked", self.open_log_folder)
        self.hbox.pack_end(button, False, False, 10)

        self.vbox.pack_end(self.hbox, False, False, 10)
        self.show_all()

    def on_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.search_entry.emit("stop-search")
            return

        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval == Gdk.KEY_f:
            self.attach_search_entry()
            return

        shift = (event.state & Gdk.ModifierType.SHIFT_MASK)
        if event.keyval == Gdk.KEY_Return:
            if shift:
                self.search_entry.emit("previous-match")
            else:
                self.search_entry.emit("next-match")

    def attach_search_entry(self):
        self.search_entry.grab_focus()
        if len(self.search_entry.get_text()) > 0:
            self.logtextview.find_first(self.search_entry)

    def dettach_search_entry(self, searched_entry):
        if self.search_entry.props.parent is not None:
            self.logtextview.reset_search()
            self.logtextview.grab_focus()

    def clear_log(self, _widget):
        self.buffer.set_text("")

    def save_log(self, _widget):
        log_name = "{}_{}-{}-{}_{}:{}:{}.log".format(self.game_title, datetime.datetime.today().year,
                                                     datetime.datetime.today().month, datetime.datetime.today().day,
                                                     datetime.datetime.now().hour, datetime.datetime.now().minute,
                                                     datetime.datetime.now().second)
        if not system.path_exists(LOG_PATH):
            system.create_folder(LOG_PATH)
        with open(os.path.join(LOG_PATH, log_name), "w") as log_file:
            log_file.write(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), False))

    @staticmethod
    def open_log_folder(_widget):
        if not system.path_exists(LOG_PATH):
            system.create_folder(LOG_PATH)
        open_uri("file://%s" % LOG_PATH)

