#!/usr/bin/python

"""
Thread to establish the connection with the robot
"""
__author__ = 'Nicola Covallero'

from PyQt4 import QtCore

class ConnectToRobot(QtCore.QThread):
    # reference: http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
    connection_done = QtCore.pyqtSignal(object) # this is a signal

    def __init__(self, GUI):
        """
        :param GUI: the main window
        """
        QtCore.QThread.__init__(self)
        self.GUI = GUI # main window

    def run(self):
        self.GUI.print_("\n --------------------------------------------- \n CONNECTING TO JONNY ROBOT ")
        self.GUI.print_(" ---------------------------------------------")
        self.GUI.print_ ("The current IP saved in the system is: " + str(self.GUI.IP))

        IP =self.GUI.IP

        self.GUI.print_('Testing IP address: ' + str(IP))

        # 1st test: here we try to connect using the current IP address
        msg = "connected"
        self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
        [success, data] = self.GUI.connection_socket.receiveData(
            timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
        if success:
            if data[0] == msg:
                self.GUI.IP = data[1]
                # double check the IP address
                self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
                [success, data] = self.GUI.connection_socket.receiveData(
                    timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
                if success:
                    if data[0] == msg and self.GUI.IP == data[1]:
                        self.GUI.IP = data[1][0]
                        self.GUI.print_("The IP address of Jonnhy Robot is " + str(IP)) # print in the text log
                        self.connection_done.emit(True) # emit a signal with a boolean variable True
                        return

        # test all the IP address from 0 -> 100 The format will be 192.168.1.#
        for i in range(0, 100):
            IP = "192.168.1." + str(i)

            self.GUI.print_('Testing IP address: ' + IP)

            msg = "connected"
            self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
            [success, data] = self.GUI.connection_socket.receiveData(
                timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
            if success:
                if data[0] == msg:
                    self.GUI.IP = data[1][0]
                    # double check the IP address
                    self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
                    [success, data] = self.GUI.connection_socket.receiveData(
                        timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
                    if success:
                        if data[0] == msg and self.GUI.IP == data[1][0]:
                            self.GUI.IP = data[1][0]
                            self.GUI.print_("The IP address of Jonnhy Robot is " + IP)
                            self.connection_done.emit(True)
                            break

        if IP == "192.168.1.99":
            self.GUI.print_("Failed  to connect to jonny robot, either it is turn off or not UDP socket has been created")
            self.connection_done.emit(False)