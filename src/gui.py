#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Nicola Covallero

Simple GUI for my robot.
This is a test, the GUI should work in ROS
"""

# https://pythonspot.com/en/pyqt4/

import os, sys
from PyQt4 import QtGui, QtCore
import cv
import communication

class JRI(QtGui.QWidget):#inheretid qtgui

    def __init__(self):
        super(JRI, self).__init__()

        self.max_speed = 10

        self.initUI() #creation of the gui

        self.camera_index = 0
        self.capture = cv.CaptureFromCAM(self.camera_index)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 720)

        self.connected_to_RP = False

        self.IP = ""

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
        self.timer.timeout.connect(self.updateImage)

        btn = QtGui.QPushButton('Close Button', self)
        btn.setToolTip('Close the GUI')
        #btn.clicked.connect(QtCore.QCoreApplication.instance().quit) # connect to the quit function
        btn.clicked.connect(self.closeButtonEvent)
        btn.resize(btn.sizeHint())
        btn.move(640, 0)

        pbtn = QtGui.QPushButton('Connect', self)
        pbtn.setToolTip('Connect to the Raspberry by testing all the possible IPs')
        pbtn.clicked.connect(self.connect)
        pbtn.resize(btn.sizeHint())
        pbtn.move(640, btn.height())

        # SLIDER
        self.sld = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.sld.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sld.setGeometry(640,pbtn.height() + btn.height() , 30,100)
        self.sld.valueChanged[int].connect(self.changeValue)
        self.sld.setMinimum(0)
        self.sld.setMaximum(self.max_speed)
        self.sld.setValue(2)
        self.sld.setTickInterval(10)
        self.sld.setTickPosition(QtGui.QSlider.TicksLeft)

        # VELOCITY LABEL (Connectede to slider)
        self.velocity_label = QtGui.QLabel(self)
        self.velocity_label.setText('Velocity: \n' + str(self.sld.value()))
        self.velocity_label.setGeometry(640 + self.sld.width(), pbtn.height() + btn.height() , 100,100)

        # sonar pic
        self.sonar_pic = QtGui.QLabel(self)
        self.sonar_pic.setGeometry(640, pbtn.height() + btn.height() + self.sld.height() + 10, 90, 59)
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
        # ---------------------------------------------------------




        # MAIN WINDOW
        self.setGeometry(300, 300, 640 + btn.width(), 510)# size + position of the widget
        self.center()
        self.setWindowTitle('JRI - Jonny Robot Interface')
        self.setWindowIcon(QtGui.QIcon('img/jri_logo.png'))
        self.show()

        # ------------- Secodnary Windows
        self.settingsWindow = SettingsWindow(self)

    def changeValue(self, value):
        str_ = 'Velocity: \n' + str(value)
        self.velocity_label.setText(str_)

    def connect(self):

        print "The current IP saved in the system is: ", self.IP

        timeout = 0.05
        self.udp_socket = communication.Communication()

        IP = self.IP

        print 'Testing IP address: ', IP

        msg = "connected"
        self.udp_socket.sentData(msg, IP)
        [success, data] = self.udp_socket.receiveData(
            timeout=timeout)  # do not put it too fast, otherwise the IP is wrong
        if success:
            if data[0] == msg:
                self.IP = data[1]
                # double check the IP address
                self.udp_socket.sentData(msg, IP)
                [success, data] = self.udp_socket.receiveData(
                    timeout=timeout)  # do not put it too fast, otherwise the IP is wrong
                if success:
                    if data[0] == msg and self.IP == data[1]:
                        self.IP = data[1][0]
                        print "The IP address of Jonnhy Robot is", IP
                        return

        for i in range(0,100):
            IP = "192.168.1." + str(i)

            print 'Testing IP address: ', IP

            msg = "connected"
            self.udp_socket.sentData(msg,IP)
            [success,data] = self.udp_socket.receiveData(timeout=timeout) # do not put it too fast, otherwise the IP is wrong
            if success:
                if data[0] == msg:
                    self.IP = data[1]
                    # double check the IP address
                    self.udp_socket.sentData(msg, IP)
                    [success, data] = self.udp_socket.receiveData(timeout=timeout)  # do not put it too fast, otherwise the IP is wrong
                    if success:
                        if data[0] == msg and self.IP == data[1]:
                            self.IP = data[1][0]
                            print "The IP address of Jonnhy Robot is", IP
                            break

        if IP == "192.168.1.99":
            print "Failed  to connect to jonny robot, either it is turn off or not UDP socket has been created"

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

    def updateImage(self):
        self.frame = cv.QueryFrame(self.capture)
        self.resize_frame = cv.CreateMat(480, 640, cv.CV_8UC3)
        cv.Resize(self.frame, self.resize_frame)
        image = QtGui.QImage(self.resize_frame.tostring(), self.resize_frame.width, self.resize_frame.height, QtGui.QImage.Format_RGB888).rgbSwapped()

        pixmap = QtGui.QPixmap.fromImage(image)
        self.pic.setPixmap(pixmap)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_W:
            print 'pressed W'
        elif e.key() == QtCore.Qt.Key_S:
            print 'pressed S'
        elif e.key() == QtCore.Qt.Key_A:
            print 'pressed A'
        elif e.key() == QtCore.Qt.Key_D:
            print 'pressed D'
        elif e.key() == QtCore.Qt.Key_Minus:
            print 'Reducing speed'
            self.sld.setValue(self.sld.value() - 1)
        elif e.key() == QtCore.Qt.Key_Plus:
            print 'Increasing speed'
            self.sld.setValue(self.sld.value() + 1)
        """
        NOTE: to make a 2 key press you have to set for each keypress save the key,
        and if it is realeased delete it
        """

    @QtCore.pyqtSlot()
    def openSettings(self):
        print 'Opening settings'
        self.settingsWindow.IP_input.setText(str(self.IP))
        self.settingsWindow.exec_()
        pass

# reference: http://stackoverflow.com/questions/13517568/how-to-create-new-pyqt4-windows-from-an-existing-window
class SettingsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.IP = ""
        self.initUI()
        self.parent = parent


    def initUI(self):

        self.apply_btn = QtGui.QPushButton("Apply")
        self.apply_btn.clicked.connect(self.applyChanges)
        #self.btn.clicked.connect(self.getItem)
        layout = QtGui.QFormLayout()
        layout.addRow(self.apply_btn)
        self.IP_label = QtGui.QLabel(self)
        self.IP_label.setText('IP:')
        self.IP_input = QtGui.QLineEdit()
        self.IP_input.setText(self.IP)
        layout.addRow(self.IP_label, self.IP_input)
        self.setLayout(layout)

        # MAIN WINDOW
        self.setGeometry(300, 300, 300, 300)
        self.setWindowIcon(QtGui.QIcon('img/Settings-L-icon.png'))
        self.setWindowTitle('Settings')

    def applyChanges(self):

        self.parent.IP = self.IP_input.text()
        self.close()


def main():

    app = QtGui.QApplication(sys.argv)
    ex = JRI()
    sys.exit(app.exec_())# loop

if __name__ == '__main__':
    main()