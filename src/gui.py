#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Nicola Covallero

Simple GUI for my robot.
"""

# https://pythonspot.com/en/pyqt4/

import os, sys
from PyQt4 import QtGui, QtCore
import cv, cv2
import udpsocket
import time
import matplotlib.image as mpimg
from PIL import Image
import numpy


class JRI(QtGui.QWidget):
    # TODO create docstrings
    def __init__(self):


        super(JRI, self).__init__()
        self.counter = 1 # silly thing, only for testing in the UpdateImage method
        self.image = 1 # the same of the one above
        # properties
        self.max_speed = 100
        self.min_speed = 70
        self.timeout = 0.05 # timeout for the socket test conection

        self.udp_socket = udpsocket.UDPSocket()

        self.time_last_frame = 0

        # self.camera_index = 0
        # self.capture = cv.CaptureFromCAM(self.camera_index)
        # cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
        # cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 720)

        self.connected_to_RP = False

        self.IP = ""

        # set properties for the buttons
        self.w_pressed = False
        self.w_released = True
        self.a_pressed = False
        self.a_released = True
        self.s_pressed = False
        self.s_released = True
        self.d_pressed = False
        self.d_released = True
        self.minus_pressed = False
        self.minus_released = True
        self.plus_pressed = False
        self.plus_released = True

        self.picamera_frame = Image.open('img/jri_logo.png')
        self.connection_port = 2525
        self.connected_to_robot = False
        self.initUI()  # creation of the gui


    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))


        # ref: http://stackoverflow.com/questions/29807201/update-qwidget-every-minutes
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)  # 200ms of interval
        self.timer.start(0)

        self.setToolTip('This is a GUI developed in PyQt for the Jonny Robot. (STILL IN DEVELOPMENT')

        # image
        self.pic = QtGui.QLabel(self)
        self.pic.setGeometry(0, 0, 640, 480)
        # use full ABSOLUTE path to the image, not relative
        self.pic.setPixmap(QtGui.QPixmap(os.getcwd() + "/img/logo.png"))
        self.pic.setToolTip('Image seen by the webcam')
        #self.timer.timeout.connect(self.updateImageCV)
        self.timer.timeout.connect(self.updateImage)
        self.timer.timeout.connect(self.updateKeys)


        self.btn = QtGui.QPushButton('Exit', self)
        self.btn.setToolTip('Close the GUI')
        #self.btn.clicked.connect(QtCore.QCoreApplication.instance().quit) # connect to the quit function
        self.btn.clicked.connect(self.closeButtonEvent)
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(640, 0)

        self.pbtn = QtGui.QPushButton('Connect', self)
        self.pbtn.setStyleSheet("background-color: red")
        self.pbtn.setToolTip('Connect to the Raspberry by testing all the possible IPs')
        self.pbtn.clicked.connect(self.connect)
        self.pbtn.resize(self.btn.sizeHint())
        self.pbtn.move(640, self.btn.height())

        # SLIDER
        self.sld = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.sld.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sld.setGeometry(640,self.pbtn.height() + self.btn.height() , 30,100)
        self.sld.setMinimum(self.min_speed)
        self.sld.setMaximum(self.max_speed)
        self.sld.setValue((self.max_speed + self.min_speed)/2)
        self.sld.setTickInterval(50)
        self.sld.setTickPosition(QtGui.QSlider.TicksLeft)
        # VELOCITY LABEL (Connectede to slider)
        self.velocity_label = QtGui.QLabel(self)
        self.velocity_label.setText('Velocity: \n' + str(self.sld.value()))
        self.velocity_label.setGeometry(640 + self.sld.width(), self.pbtn.height() + self.btn.height(), 100, 100)
        self.velocity_label.setToolTip('PWM value')
        self.sld.valueChanged[int].connect(self.changeValue)

        # sonar pic
        self.sonar_pic = QtGui.QLabel(self)
        self.sonar_pic.setGeometry(640, self.pbtn.height() + self.btn.height() + self.sld.height() + 10, 90, 59)
        # use full ABSOLUTE path to the image, not relative
        self.sonar_pic.setPixmap(QtGui.QPixmap(os.getcwd() + "/img/sonar_cropped2.png"))
        self.sonar_pic.setToolTip('Sonar')

        # self.statusBar = QtGui.QStatusBar(self)
        # self.statusBar.showMessage('Ready')
        # self.statusBar.setGeometry(480, 0, 100, 20)



        # --------------- SIMPLE MENUBAR --------------------------
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(0, 480, 200, 50)

        self.fileMenu = self.menubar.addMenu('&File')
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        self.fileMenu.addAction(exitAction)

        #self.fileMenu = self.menubar.addMenu('&Settings')
        settingsAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Settings', self)
        settingsAction.setShortcut('Ctrl+O')
        settingsAction.setStatusTip('Open settings')
        settingsAction.triggered.connect(self.openSettings)
        self.fileMenu.addAction(settingsAction)

        testAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&TestThread', self)
        testAction.triggered.connect(self.getData)
        self.fileMenu.addAction(testAction)
        # ---------------------------------------------------------

        # Text Log ------------------------------------------------
        self.textLog = QtGui.QTextEdit(self)
        self.textLog.setReadOnly(True)
        self.textLog.setGeometry(0, 530, 640 + self.btn.width(), 100)
        self.textLog.ensureCursorVisible()
        self.textLog.setToolTip('Text log, It shows relevant information of the system.')
        # ---------------------------------------------------------

        # MAIN WINDOW
        window_width = 640 + self.btn.width()
        window_height = 630
        self.setGeometry(300, 300, window_width , window_height)# size + position of the widget
        self.center()
        self.setWindowTitle('JRI - Jonny Robot Interface')
        self.setWindowIcon(QtGui.QIcon('img/jri_logo.png'))
        self.setFixedSize(window_width,window_height)
        self.show()

        # ------------- Secodnary Windows
        self.settingsWindow = SettingsWindow(self)

    def changeValue(self, value):
        str_ = 'Velocity: \n' + str(value)
        self.velocity_label.setText(str_)

    def connect(self):
        self.threads = []  # <---- IMPORTANT TO PUT
        connection = ConnectToRobot(self)
        connection.connection_done.connect(self.update_connection)
        self.threads.append(connection)
        connection.start()

    def closeEvent(self, event):# this is the reimplementation of the default closeEvent of QtGui

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def closeButtonEvent(self, event):  # this is the reimplementation of the default closeEvent of QtGui

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            QtCore.QCoreApplication.instance().quit()


    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def updateImageCV(self):
        self.frame = cv.QueryFrame(self.capture)
        self.resize_frame = cv.CreateMat(480, 640, cv.CV_8UC3)
        cv.Resize(self.frame, self.resize_frame)
        image = QtGui.QImage(self.resize_frame.tostring(), self.resize_frame.width, self.resize_frame.height, QtGui.QImage.Format_RGB888).rgbSwapped()

        pixmap = QtGui.QPixmap.fromImage(image)
        self.pic.setPixmap(pixmap)

    def PIL2array(self,img):
        return numpy.array(img.getdata(),
                           numpy.uint8).reshape(img.size[1], img.size[0], 3)

    def updateImage(self):

        #self.counter = self.counter + 1
        #print "updating Image", self.counter

        # silly thing just to see how fast is, changing mage each iteration

        #if self.image == 1:
        #    pi = Image.open('img/tux.jpg')
        #    self.image = 2
        #else:
        #    pi = Image.open('img/jri_logo.png')
        #    self.image = 1

        # we skip the conversion process by transforming the image directly from the QImage
        #self.frame = cv.fromarray(numpy.asarray(pi).astype(numpy.uint8))
        #print "frame size", self.frame.channels
        #self.resize_frame = cv.CreateMat(480, 640, self.frame.type)#
        #cv.Resize(self.frame, self.resize_frame)
        #self.resize_frame =  numpy.array(self.resize_frame)

        # print self.resize_frame.shape
        time_ = time.time()
        pi = self.picamera_frame
        a = numpy.asarray(pi).astype(numpy.uint32)
        # we know pack the RGB values (also the Alpha channel if it exists (PNG))
        # They have to be pucked accordingly to the Format of the QImage, in pour case ARGB32
        # which means 32 bits where: 8 bites (alpha) - 8 bites (red) - 8 bites (green) - 8 bites (blue)
        # if the file has no alpha is better to put a fake one.
        if a.shape[2] == 4:
            b = (  a[:, :, 3] << 24 | a[:, :, 0] << 16 | a[:, :, 1] << 8 | a[:, :, 2]).flatten()
        else:
            b = ( 255 << 24 | a[:, :, 0] << 16 | a[:, :, 1] << 8 | a[:, :, 2]).flatten()
        image = QtGui.QImage(b, a.shape[1], a.shape[0], QtGui.QImage.Format_ARGB32)
        size = QtCore.QSize(640,480)
        image = image.scaled(size)

        #
        # image = QtGui.QImage(self.resize_frame.shape[1],self.resize_frame.shape[0], QtGui.QImage.Format_RGB888)
        #
        # for x in range(0,self.resize_frame.shape[1]):
        #     for y in range(0, self.resize_frame.shape[0]):
        #         c = QtGui.QColor(self.resize_frame[y][x][0],self.resize_frame[y][x][1],self.resize_frame[y][x][2])
        #         image.setPixel(x,y,c.rgb())
        # print "To convert the image took", time.time() - time_

        #cv2.imshow('image', a.astype(numpy.uint8))
        #cv2.waitKey()

        pixmap = QtGui.QPixmap.fromImage(image)

        self.pic.setPixmap(pixmap)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_W:
            #self.print_('pressed W')
            self.w_pressed = True
            self.w_released = False
        elif e.key() == QtCore.Qt.Key_S:
            # self.print_( 'pressed S')
            self.s_pressed = True
            self.s_released = False
        elif e.key() == QtCore.Qt.Key_A:
            # self.print_( 'pressed A')
            self.a_pressed = True
            self.a_released = False
        elif e.key() == QtCore.Qt.Key_D:
            # self.print_( 'pressed D')
            self.d_pressed = True
            self.d_released = False
        elif e.key() == QtCore.Qt.Key_Minus:
            # self.print_( 'Reducing speed')
            self.minus_pressed = True
            self.minus_released = False
            #self.sld.setValue(self.sld.value() - 1)
        elif e.key() == QtCore.Qt.Key_Plus:
            # self.print_( 'Increasing speed')
            self.plus_pressed = True
            self.plus_released = False
            #self.sld.setValue(self.sld.value() + 1)

        """
        NOTE: to make a 2 key press you have to set for each keypress save the key,
        and if it is realeased delete it
        """


    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_W:
            self.w_pressed = False
            self.w_released = True
        elif e.key() == QtCore.Qt.Key_S:
            self.s_pressed = False
            self.s_released = True
        elif e.key() == QtCore.Qt.Key_A:
            self.a_pressed = False
            self.a_released = True
        elif e.key() == QtCore.Qt.Key_D:
            self.d_pressed = False
            self.d_released = True
        elif e.key() == QtCore.Qt.Key_Minus:
            self.minus_pressed = False
            self.minus_released = True
        elif e.key() == QtCore.Qt.Key_Plus:
            self.plus_pressed = False
            self.plus_released = True

    def updateKeys(self):
        if self.w_pressed and not self.w_released:
            self.print_('W pressed')
        if self.a_pressed and not self.a_released:
            self.print_('A pressed')
        if self.d_pressed and not self.d_released:
            self.print_('D pressed')
        if self.s_pressed and not self.s_released:
            self.print_('S pressed')

    @QtCore.pyqtSlot()
    def openSettings(self):
        print 'Opening settings'
        self.settingsWindow.IP_input.setText(str(self.IP))
        self.settingsWindow.exec_()
        pass

    def getData(self):
        # TODO these two sockets are the same and are waiting for different data, we should use just one
        # and add a code to specify the kind of data it has been sent
        # When we send a data we can specify the kind of port (In the rasp the socket has been binded)
        # We could do here a similar thing creating two sockets only for riceiving
        # http://stackoverflow.com/questions/8994937/send-image-using-socket-programming-python

        self.threads = [] # <---- IMPORTANT TO PUT
        receiveDataSonar = ReceiveData(self.udp_socket,self.timeout)
        receiveDataSonar.data_received.connect(self.data_received_sonar)
        self.threads.append(receiveDataSonar)
        #receiveDataSonar.start()

        receiveDatacamera = ReceiveData(self.udp_socket, self.timeout, 40*8192)
        receiveDatacamera.data_received.connect(self.data_received_camera)
        self.threads.append(receiveDatacamera)
        receiveDatacamera.start()

    def data_received_sonar(self,data):
        if self.IP == data[1][0]:
            self.sonar_dist = float(data)

    def data_received_camera(self, data):
        if self.IP == data[1][0]:
            print "received data"
            #self.picamera_frame = cv.fromarray(data)
            self.picamera_frame = data
            self.time_last_frame = time.time()

    def update_connection(self, data):
        self.connected_to_robot = data
        print 'Data: ', data
        if data:
            self.pbtn.setStyleSheet("background-color: green")
        else:
            self.pbtn.setStyleSheet("background-color: red")

    def print_(self,text):
        print text
        self.textLog.append(text)
        self.textLog.moveCursor(QtGui.QTextCursor.End)



# reference: http://stackoverflow.com/questions/13517568/how-to-create-new-pyqt4-windows-from-an-existing-window
class SettingsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.IP = ""
        self.parent = parent
        self.initUI()


    def initUI(self):

        self.apply_btn = QtGui.QPushButton("Apply")
        self.apply_btn.clicked.connect(self.applyChanges)
        self.cancel_btn = QtGui.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancelBtn)
        #self.btn.clicked.connect(self.getItem)
        layout = QtGui.QFormLayout()
        layout.addRow(self.cancel_btn, self.apply_btn)

        # IP address -----------------------------
        self.IP_label = QtGui.QLabel(self)
        self.IP_label.setText('IP:')
        self.IP_input = QtGui.QLineEdit()
        self.IP_input.setText(self.IP)
        layout.addRow(self.IP_label, self.IP_input)
        # ----------------------------------------

        # minimum velocity -----------------------
        self.min_speed_label = QtGui.QLabel(self)
        self.min_speed_label.setText('Minimum speed:')
        self.min_speed_label.setToolTip('Minimum PWM value to make the motors work. This should be tune for each Robot (pair of motors )')
        self.min_speed_input = QtGui.QLineEdit()
        self.min_speed_input.setText(str(self.parent.min_speed))
        layout.addRow(self.min_speed_label, self.min_speed_input)
        # ----------------------------------------

        # minimum velocity -----------------------
        self.timeout_label = QtGui.QLabel(self)
        self.timeout_label.setText('Timeout:')
        self.timeout_label.setToolTip(
            'Timeout value for testing the connection with RPI, bigger it is better it is, but more time to find the Jonny Robot in the Network')
        self.timeout_input = QtGui.QLineEdit()
        self.timeout_input.setText(str(self.parent.timeout))
        layout.addRow(self.timeout_label, self.timeout_input)
        # ----------------------------------------


        # MAIN WINDOW
        self.setLayout(layout)
        self.setGeometry(300, 300, 300, 300)
        self.setWindowIcon(QtGui.QIcon('img/Settings-L-icon.png'))
        self.setWindowTitle('Settings')

    def applyChanges(self):

        self.parent.IP = self.IP_input.text()
        self.parent.min_speed = int(self.min_speed_input.text())
        self.parent.sld.setMinimum(self.parent.min_speed)
        self.parent.timeout = float(self.timeout_input.text())
        self.close()

    def cancelBtn(self):
        self.close()


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


class ConnectToRobot(QtCore.QThread):
    # reference: http://stackoverflow.com/questions/9957195/updating-gui-elements-in-multithreaded-pyqt
    connection_done = QtCore.pyqtSignal(object) # this is a signal

    def __init__(self, GUI):
        QtCore.QThread.__init__(self)
        self.GUI = GUI # main window

    def run(self):
        self.GUI.print_("\n --------------------------------------------- \n CONNECTING TO JONNY ROBOT ")
        self.GUI.print_(" ---------------------------------------------")
        self.GUI.print_ ("The current IP saved in the system is: " + str(self.GUI.IP))

        IP =self.GUI.IP

        self.GUI.print_('Testing IP address: ' + str(IP))

        msg = "connected"
        self.GUI.udp_socket.sendData(msg, IP=IP, port=self.GUI.connection_port)
        [success, data] = self.GUI.udp_socket.receiveData(
            timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
        if success:
            if data[0] == msg:
                self.GUI.IP = data[1]
                # double check the IP address
                self.GUI.udp_socket.sendData(msg, IP=IP, port=self.GUI.connection_port)
                [success, data] = self.GUI.udp_socket.receiveData(
                    timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
                if success:
                    if data[0] == msg and self.GUI.IP == data[1]:
                        self.GUI.IP = data[1][0]
                        self.GUI.print_("The IP address of Jonnhy Robot is " + str(IP))
                        self.connection_done.emit(True)
                        return

        for i in range(0, 100):
            IP = "192.168.1." + str(i)

            self.GUI.print_('Testing IP address: ' + IP)

            msg = "connected"
            self.GUI.udp_socket.sendData(msg, IP=IP, port=self.GUI.connection_port)
            [success, data] = self.GUI.udp_socket.receiveData(
                timeout=self.GUI.timeout)  # do not put it too fast, otherwise the IP is wrong
            if success:
                if data[0] == msg:
                    self.GUI.IP = data[1][0]
                    # double check the IP address
                    self.GUI.udp_socket.sendData(msg, IP=IP, port=self.GUI.connection_port)
                    [success, data] = self.GUI.udp_socket.receiveData(
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


def main():

    app = QtGui.QApplication(sys.argv)
    ex = JRI()
    sys.exit(app.exec_())# loop

if __name__ == '__main__':
    main()