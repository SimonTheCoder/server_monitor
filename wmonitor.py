#!/usr/bin/python


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from monitor import Monitor


def refresh_host(server_list_file = None):
    if server_list_file is None:
        server_list_file = "servers.list"
    
    list_store = builder.get_object("host_ListStore")

    list_store.clear() 
    #list_store.append([True,"a","1.1.1.1",3.14159])
    list_store.append([False,"refresh ...","",0])

    #window.queue_draw()

    file_chooser = builder.get_object("server_list_file_chooser")
    server_list_file = file_chooser.get_filename()
    if server_list_file is None:
        server_list_file = "server.list"
        file_chooser.set_filename(server_list_file)
    print "chooser: " + server_list_file
    m = Monitor(server_list_file)
    print "%d servers in list." % len(m.server_list)
    results = m.check_all()
    list_store.clear()

    for i in results:
        list_store.append([i.state == i.SERVER_STATE_UP,i.host,i.ip,i.time])
    print(len(list_store))


class Handler:
    def onButtonClick(self, button):
        print "refresh clicked."
        #Gtk.main_quit()
        refresh_host()
    def onCopy1stIP(self, button):
        print "copy to clipboard."
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        list_store = builder.get_object("host_ListStore")
        clipboard.set_text(list_store[0][2], -1)

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onIpEdited(self,arg1, arg2, arg3):
        print "ip clicked"

    def onServerFileChoosed(self, *args):
        print "file choosed"
builder = Gtk.Builder()
builder.add_from_file("monitor_ui.glade")
builder.connect_signals(Handler())

window = builder.get_object("main_window")
#window = builder.get_object("window2")
window.show_all()

Gtk.main()

