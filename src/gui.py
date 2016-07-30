#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Nicola Covallero

Simple GUI for my robot.
A nice tutorial: http://www.python.it/wiki/show/qttutorial/
"""

# https://pythonspot.com/en/pyqt4/

import os, sys
from PyQt4 import QtGui, QtCore
import settingswindow, connection2robot, receivedata
import cv, cv2
import udpsocket
import time
from PIL import Image
import numpy




class JRI(QtGui.QWidget):
    # TODO create docstrings
    def __init__(self):

        super(JRI, self).__init__()

        # properties
        self.max_speed = 100
        self.min_speed = 70
        self.timeout = 0.05 # timeout for the socket test conection
        self.speed = 0 # TODO: use it
        self.communication_style = 'WIFI' # WIFI or BLUETOOTH


        # COMMUNICATIONS --------------------------------------------
        # Socket used only to establish connection with the robot
        self.connection_socket = udpsocket.UDPSocket()
        self.CONNECTION_PORT = 2525

        self.driving_socket = udpsocket.UDPSocket()
        self.DRIVING_PORT = 2526
        # -----------------------------------------------------------

        self.time_last_frame = 0

        self.connected_to_robot = False
        self.IP = ""

        # set properties for the buttons -----------------
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
        # ------------------------------------------------

        # Default image when no image is received
        self.picamera_frame = Image.open('../img/jri_logo.png')


        # save the threads
        self.threads = []  # <---- IMPORTANT TO PUT

        self.initUI()  # creation of the gui

    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        layout = QtGui.QFormLayout()


        # ref: http://stackoverflow.com/questions/29807201/update-qwidget-every-minutes
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)  # 200ms of interval
        self.timer.start(0)

        # set tooltip of the GUI
        self.setToolTip('This is a GUI developed in PyQt for the Jonny Robot. (STILL IN DEVELOPMENT')

        # # --------------- SIMPLE MENUBAR --------------------------
        # self.menubar = QtGui.QMenuBar(self)
        # #self.menubar.setGeometry(0, 480, 200, 50)
        #
        # self.fileMenu = self.menubar.addMenu('&File')
        # exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        # exitAction.setShortcut('Ctrl+Q')
        # exitAction.setStatusTip('Exit application')
        # exitAction.triggered.connect(QtGui.qApp.quit)
        # self.fileMenu.addAction(exitAction)
        #
        # #self.fileMenu = self.menubar.addMenu('&Settings')
        # settingsAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Settings', self)
        # settingsAction.setShortcut('Ctrl+O')
        # settingsAction.setStatusTip('Open settings')
        # settingsAction.triggered.connect(self.openSettings)
        # self.fileMenu.addAction(settingsAction)
        #
        # testAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&TestThread', self)
        # testAction.triggered.connect(self.getData)
        # self.fileMenu.addAction(testAction)
        # # ---------------------------------------------------------

        quit = QtGui.QAction(QtGui.QIcon("../img/cancel.ico"), "Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Quit application")
        quit.triggered.connect(self.closeButtonEvent)
        settings = QtGui.QAction(QtGui.QIcon("../img/Settings-L-icon.png"), "Settings", self)
        settings.setShortcut("Ctrl+O")
        settings.setStatusTip("Settings window")
        settings.triggered.connect(self.openSettings)
        self.connection = QtGui.QAction(QtGui.QIcon("../img/wifi-icon-off.png"), "Connect", self)
        self.connection.setShortcut("Ctrl+C")
        self.connection.setToolTip("Connect to the robot - OFF")
        self.connection.triggered.connect(self.connect)

        # image
        self.pic = QtGui.QLabel(self)
        self.pic.resize(640,480)
        # use full ABSOLUTE path to the image, not relative
        self.pic.setPixmap(QtGui.QPixmap(os.getcwd() + "/img/logo.png"))
        self.pic.setToolTip('Image seen by the webcam')
        self.pic.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        #self.timer.timeout.connect(self.updateImageCV)
        self.timer.timeout.connect(self.updateImage)
        self.timer.timeout.connect(self.updateKeys)

        # SLIDER
        self.sld = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.sld.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sld.setFixedHeight(200)
        self.sld.setMinimum(self.min_speed)
        self.sld.setMaximum(self.max_speed)
        self.sld.setValue((self.max_speed + self.min_speed)/2)
        self.sld.setTickInterval(50)
        self.sld.setTickPosition(QtGui.QSlider.TicksLeft)

        # VELOCITY LABEL (Connected to slider)
        self.velocity_label = QtGui.QLabel(self)
        self.velocity_label.setText('Velocity: \n' + str(self.sld.value()))
        #self.velocity_label.setGeometry(640 + self.sld.width(), self.pbtn.height() + self.btn.height(), 100, 100)
        self.velocity_label.setToolTip('PWM value')
        self.sld.valueChanged[int].connect(self.changeValue)



        # Text Log ------------------------------------------------
        self.textLog = QtGui.QTextEdit(self)
        self.textLog.setReadOnly(True)
        #self.textLog.setGeometry(0, 530, 640 + self.btn.width(), 100)
        self.textLog.ensureCursorVisible()
        self.textLog.setToolTip('Text log, It shows relevant information of the system.')
        # ---------------------------------------------------------

        # MAIN WINDOW - Layout Definition -------------------------
        grid = QtGui.QGridLayout(self)

        # toolbar
        toolbar = QtGui.QToolBar(self)
        toolbar.addAction(quit)
        toolbar.addAction(settings)
        toolbar.addAction(self.connection)
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)


        grid.addWidget(toolbar, 0, 0)
        grid.addWidget(self.pic,1,0)

        vbox1 = QtGui.QVBoxLayout()
        hbox_speed = QtGui.QHBoxLayout()
        hbox_speed.addWidget(self.sld)
        hbox_speed.addWidget(self.velocity_label)
        vbox1.addLayout(hbox_speed)

        # sonar pic
        self.sonar_pic = QtGui.QLabel(self)
        # use full ABSOLUTE path to the image, not relative
        self.sonar_pic.setPixmap(QtGui.QPixmap(os.getcwd() + "../img/sonar_cropped2.png"))
        self.sonar_pic.setToolTip('Sonar')
        vbox1.addWidget(self.sonar_pic)
        vbox1.setAlignment(self.sonar_pic, QtCore.Qt.AlignBottom)

        grid.addLayout(vbox1,0,1,2,1)
        grid.addWidget(self.textLog,2,0,2,2)

        self.setLayout(grid)
        self.move(100,50)
        self.setWindowTitle('JRI - Jonny Robot Interface')
        self.setWindowIcon(QtGui.QIcon('../img/jri_logo.png'))
        self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        #self.setFixedSize(self.width(), self.height()) # fixed size
        #self.setFixedSize(self.sizeHint())
        self.show()

    def changeValue(self, value):
        """
        Change value of the speed accordingly to the slidebar
        :param value:
        :return:
        """
        str_ = 'Velocity: \n' + str(value)
        self.speed = value
        self.velocity_label.setText(str_)

    def connect(self):
        """
        Connect to the robot
        :return:
        """
        connection = connection2robot.ConnectToRobot(self)
        connection.connection_done.connect(self.update_connection) # this is called when a signal is emitted by such a thread
        self.threads.append(connection)
        connection.start() # start the thread

    def closeEvent(self, event):# this is the reimplementation of the default closeEvent of QtGui
        """
        Message window before to close
        :param event:
        :return:
        """
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def closeButtonEvent(self, event):  # this is the reimplementation of the default closeEvent of QtGui
        """
        Close button event.
        :param event:
        :return:
        """

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            QtCore.QCoreApplication.instance().quit()


    def center(self):
        """
        Center the window in the display
        :return:
        """

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def updateImageCV(self):
        """
        Update the image in the case the image is provided as IplImage (only for test this will be deleted)
        :return:
        """
        self.frame = cv.QueryFrame(self.capture)
        self.resize_frame = cv.CreateMat(480, 640, cv.CV_8UC3)
        cv.Resize(self.frame, self.resize_frame)
        image = QtGui.QImage(self.resize_frame.tostring(), self.resize_frame.width, self.resize_frame.height, QtGui.QImage.Format_RGB888).rgbSwapped()

        pixmap = QtGui.QPixmap.fromImage(image)
        self.pic.setPixmap(pixmap)

    def updateImage(self):
        """
        Update the image
        :return:
        """

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

        # the folliwng two lines are only usefull to check that the image is actually good, and that the problem is only during the QImage
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
            self.sld.setValue(self.sld.value() - 1)
        elif e.key() == QtCore.Qt.Key_Plus:
            # self.print_( 'Increasing speed')
            self.plus_pressed = True
            self.plus_released = False
            self.sld.setValue(self.sld.value() + 1)

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
            if self.connected_to_robot:
                self.driving_socket.sendData("forward-"+str(self.speed), IP=self.IP, PORT=self.DRIVING_PORT)
        if self.a_pressed and not self.a_released:
            self.print_('A pressed')
            if self.connected_to_robot:
                self.driving_socket.sendData("left-" + str(self.speed), IP=self.IP, PORT=self.DRIVING_PORT)
        if self.d_pressed and not self.d_released:
            self.print_('D pressed')
            if self.connected_to_robot:
                self.driving_socket.sendData("right-" + str(self.speed), IP=self.IP, PORT=self.DRIVING_PORT)
        if self.s_pressed and not self.s_released:
            self.print_('S pressed')
            if self.connected_to_robot:
                self.driving_socket.sendData("backward-" + str(self.speed), IP=self.IP, PORT=self.DRIVING_PORT)
        # if self.plus_pressed and not self.plus_released:
        #
        #     self.sld.setValue(self.sld.value() + 1)
        # if self.minus_pressed and not self.minus_released:
        #     self.sld.setValue(self.sld.value() - 1)

    @QtCore.pyqtSlot()
    def openSettings(self):
        self.settingsWindow = settingswindow.SettingsWindow(self) # This is important, in this way
        # we reset the window, otherwise if we open again the window we are not creating a new class but
        # visualize the window of before, which has been hidden. 
        self.settingsWindow.IP_input.setText(str(self.IP))
        self.settingsWindow.exec_()

        # update
        if self.communication_style == 'WIFI':
            img = '../img/wifi-icon-'
            if self.connected_to_robot:
                self.connection.setIcon(QtGui.QIcon(img + 'on'))
                self.connection.setToolTip("Connect to the robot - ON")
            else:
                self.connection.setIcon(QtGui.QIcon(img + 'off'))
                self.connection.setToolTip("Connect to the robot - OFF")
        elif self.communication_style == 'BLUETOOTH':
            img = '../img/bluetooth-icon-'
            if self.connected_to_robot:
                self.connection.setIcon(QtGui.QIcon(img + 'on'))
                self.connection.setToolTip("Connect to the robot - ON")
            else:
                self.connection.setIcon(QtGui.QIcon(img + 'off'))
                self.connection.setToolTip("Connect to the robot - OFF")
        else:
            self.print_('ERROR: unrecognized communication style: ' + str(self.communication_style))

        pass

    def getData(self):
        """
        Get data from the raspbarry (Sonar and Camera frame)
        :return:
        """
        # TODO these two sockets are the same and are waiting for different data, we should use just one
        # and add a code to specify the kind of data it has been sent
        # When we send a data we can specify the kind of port (In the rasp the socket has been binded)
        # We could do here a similar thing creating two sockets only for riceiving
        # http://stackoverflow.com/questions/8994937/send-image-using-socket-programming-python

        self.threads = [] # <---- IMPORTANT TO PUT
        receiveDataSonar = receivedata.ReceiveData(self.connection_socket, self.timeout)
        receiveDataSonar.data_received.connect(self.data_received_sonar)
        self.threads.append(receiveDataSonar)
        #receiveDataSonar.start()

        receiveDatacamera = ReceiveData(self.connection_socket, self.timeout, 40 * 8192)
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
        print data
        if data:
            self.connection.setToolTip("Connect to the robot - ON")
            if self.communication_style == 'WIFI':
                self.connection.setIcon(QtGui.QIcon('../img/wifi-icon-on'))
            elif self.communication_style == 'BLUETOOTH':
                self.connection.setIcon(QtGui.QIcon('../img/bluetooth-icon-on'))
        else:
            self.connection.setToolTip("Connect to the robot - OFF")
            if self.communication_style == 'WIFI':
                self.connection.setIcon(QtGui.QIcon('../img/wifi-icon-off'))
            elif self.communication_style == 'BLUETOOTH':
                self.connection.setIcon(QtGui.QIcon('../img/bluetooth-icon-off'))


    def print_(self,text, terminal = True):
        """
        Print text in the terminal and in the textlog as well
        :param text:
        :param terminal: False if you do not want to print in the terminal
        :return:
        """
        if terminal: print text
        self.textLog.append(text)
        self.textLog.moveCursor(QtGui.QTextCursor.End)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = JRI()
    sys.exit(app.exec_())# loop

if __name__ == '__main__':
    main()