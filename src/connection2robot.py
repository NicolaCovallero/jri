#!/usr/bin/python

"""
Thread to establish the connection with the robot
"""
__author__ = 'Nicola Covallero'

from PyQt4 import QtCore
import bluetooth
import time

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
        if self.GUI.communication_style == "WIFI":
            self.GUI.print_("\n --------------------------------------------- \n CONNECTING TO JONNY ROBOT via WIFI")
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
                self.GUI.print_('Connection establishd with jhonny robot :) ')
                data_str = data[0].split("/")
                if data_str[0] == "jr_data":
                    self.GUI.IP = data[1][0]
                    self.GUI.yaw_angle_range = float(data_str[2])
                    self.GUI.pitch_angle_range = float(data_str[4])
                    self.GUI.print_("The IP address of Jonnhy Robot is " + str(IP))  # print in the text log
                    self.connection_done.emit(True) # emit a signal with a boolean variable True
                    return
                    # # double check the IP address
                    # self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
                    # [success, data] = self.GUI.connection_socket.receiveData(
                    #     timeout=self.GUI.timeout)  # do not set it too fast, otherwise the IP is wrong
                    # data = data.split("/")
                    # if success:
                    #     if data[0] == "jr_data" and self.GUI.IP == data[1]:
                    #         self.GUI.IP = data[1][0]
                    #         self.GUI.print_("The IP address of Jonnhy Robot is " + str(IP)) # print in the text log
                    #         self.connection_done.emit(True) # emit a signal with a boolean variable True
                    #         return

            # test all the IP address from 0 -> 100 The format will be 192.168.1.#
            for i in range(0, 100):
                IP = "192.168.0." + str(i)

                self.GUI.print_('Testing IP address: ' + IP)

                msg = "connected"
                self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
                [success, data] = self.GUI.connection_socket.receiveData(
                    timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
                if success:
                    self.GUI.print_('Connection establishd with jhonny robot :) ')
                    data_str = data[0].split("/")
                    if data_str[0] == "jr_data":
                        self.GUI.IP = data[1][0]
                        self.GUI.yaw_angle_range = float(data_str[2])
                        self.GUI.pitch_angle_range = float(data_str[4])
                        self.GUI.print_("The IP address of Jonnhy Robot is " + str(IP))  # print in the text log
                        self.connection_done.emit(True)  # emit a signal with a boolean variable True
                        return
                # if success:
                #     if data_str[0] == "jr_data" and self.GUI.IP == data[1]:
                #         self.GUI.IP = data[1][0]
                        # # double check the IP address
                        # self.GUI.connection_socket.sendData(msg, IP=IP, port=self.GUI.CONNECTION_PORT)
                        # [success, data] = self.GUI.connection_socket.receiveData(
                        #     timeout=self.GUI.timeout)  # do not set it too fast, otherwise the IP is wrong

                        # if success:
                        #     if data[0] == msg and self.GUI.IP == data[1][0]:
                        #         self.GUI.IP = data[1][0]
                        #         self.GUI.print_("The IP address of Jonnhy Robot is " + IP)
                        #         self.connection_done.emit(True)
                        #         break

            if IP == "192.168.0.99":
                self.GUI.print_("Failed  to connect to jonny robot, either it is turn off or not UDP socket has been created")
                self.connection_done.emit(False)
        elif self.GUI.communication_style == "BLUETOOTH":
            self.GUI.print_("\n --------------------------------------------- \n CONNECTING TO JONNY ROBOT via BLUETOOTH")
            self.GUI.print_(" ---------------------------------------------")
            self.GUI.print_("No address specified, looking for all the addresses")

            # here we do not do any test for the connection :P

            self.GUI.print_("Looking for DRIVING service ... ")
            if self.GUI.driving_socket_connected:
                self.GUI.driving_socket_connected = False
                # reset
                self.GUI.driving_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            driving_addr = None
            service_matches = bluetooth.find_service(uuid=self.GUI.DRIVING_SERVICE_UUID, address=driving_addr)
            #service_matches = []
            if len(service_matches)> 0:
                port = service_matches[0]["port"]
                name = service_matches[0]["name"]
                host = service_matches[0]["host"]
                driving_addr = host
                self.GUI.print_("The following service was found:")
                self.GUI.print_("port: " + str(port))
                self.GUI.print_("name: " + str(name))
                self.GUI.print_("host: " + str(host))
                self.GUI.driving_socket.connect((host,port))
                self.GUI.print_("Connection with DRIVING service established")
                self.GUI.driving_socket_connected = True
            else:
                self.GUI.print_("No DRIVING service found")
                self.connection_done.emit(False)
                return
                driving_addr = None

            #TODO handle the blueetooth sockets in a better way, resetting and so on, saving on the address
            # in order to avoid look again for the raspberry is the connection was established and still working

            time.sleep(1.0)
            self.GUI.print_("Looking for CAMERA_DRIVING service ... UUID:" + str(self.GUI.CAMERA_DRIVING_SERVICE_UUID))
            if self.GUI.camera_driving_socket_connected:
                self.GUI.camera_driving_socket_connected = False
                # reset
                self.GUI.camera_driving_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            camera_addr = None
            service_matches = bluetooth.find_service(uuid=self.GUI.CAMERA_DRIVING_SERVICE_UUID, address=camera_addr)
            if len(service_matches) > 0:
                    port = service_matches[0]["port"]
                    name = service_matches[0]["name"]
                    host = service_matches[0]["host"]
                    camera_addr = host
                    self.GUI.print_("The following service was found:")

                    self.GUI.print_("port: " + str(port))
                    self.GUI.print_("name: " + str(name))
                    self.GUI.print_("host: " + str(host))
                    self.GUI.camera_driving_socket.connect((host, port))
                    self.GUI.print_("Connection with CAMERA_DRIVING service established")
                    self.GUI.camera_driving_socket_connected = True
            else:
                self.GUI.print_("No CAMERA_DRIVING service found")
                camera_addr = None
                self.connection_done.emit(False)
                return

            self.GUI.camera_driving_socket_connected = True
            self.GUI.connected_to_robot = True
            self.connection_done.emit(True)

            pass