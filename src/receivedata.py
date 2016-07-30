#!/usr/bin/python

from PyQt4 import QtCore

class ReceiveData(QtCore.QThread):
    # reference: http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
    data_received = QtCore.pyqtSignal(object) # this is a signal

    def __init__(self, socket,timeout,buffer_size = 1024):
        QtCore.QThread.__init__(self)
        self.socket = socket
        self.timeout = timeout
        self.buffer_size = buffer_size

    def run(self):
        while 1:
            [success, data] = self.socket.receiveData(timeout=self.timeout, bufferSize = self.buffer_size)
            if success:
                print 'Data received: ' + str(data[0])
                self.data_received.emit(data)
            else:
                pass
                print 'Data NOT received'