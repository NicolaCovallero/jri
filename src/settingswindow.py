#!/usr/bin/python

"""
SettingsWindow

Windows for the settings of the GUI
"""
from __future__ import division
__author__ = 'Nicola Covallero'

from PyQt4 import QtGui, QtCore

# reference: http://stackoverflow.com/questions/13517568/how-to-create-new-pyqt4-windows-from-an-existing-window
class SettingsWindow(QtGui.QDialog):
    """
    Windows for the settings of the GUI

    The gui is passed as the 'parent' argument.
    """
    def __init__(self, parent):

        # specify the parent window(the main window in this case) of this window
        super(SettingsWindow, self).__init__(parent)

        self.IP = ""
        self.parent = parent
        self.initUI()

        self.pitch_sensibility = self.parent.pitch_sensibility
        self.yaw_sensibility = self.parent.yaw_sensibility

    def initUI(self):
        """
        Initialize the User Interface
        """

        # Buttons -----------------------------
        self.apply_btn = QtGui.QPushButton("Apply")
        self.apply_btn.clicked.connect(self.applyChanges)
        self.cancel_btn = QtGui.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancelBtn)
        #self.btn.clicked.connect(self.getItem)
        layout = QtGui.QFormLayout()
        layout.addRow(self.cancel_btn, self.apply_btn)
        # ----------------------------------------

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

        # timeout velocity -----------------------
        self.timeout_label = QtGui.QLabel(self)
        self.timeout_label.setText('Timeout:')
        self.timeout_label.setToolTip(
            'Timeout value for testing the connection with RPI, bigger it is better it is, but more time to find the Jonny Robot in the Network')
        self.timeout_input = QtGui.QLineEdit()
        self.timeout_input.setText(str(self.parent.timeout))
        layout.addRow(self.timeout_label, self.timeout_input)
        # ----------------------------------------

        # check boxes ----------------------------
        self.wifi_checkbox = QtGui.QCheckBox(self)
        self.wifi_checkbox_label = QtGui.QLabel(self)
        tooltip = 'Established the connection with the robot through WIFI'
        self.wifi_checkbox_label.setToolTip(tooltip)
        self.wifi_checkbox.setToolTip(tooltip)
        self.wifi_checkbox_label.setText('WIFI:')
        self.wifi_checkbox.setChecked(self.parent.communication_style == 'WIFI')

        self.bluetooth_checkbox = QtGui.QCheckBox(self)
        self.bluetooth_checkbox_label = QtGui.QLabel(self)
        tooltip = 'Established the connection with the robot through BLUETOOTH'
        self.bluetooth_checkbox_label.setToolTip(tooltip)
        self.bluetooth_checkbox.setToolTip(tooltip)
        self.bluetooth_checkbox_label.setText('BLUETOOTH:')
        self.bluetooth_checkbox.setChecked(self.parent.communication_style == 'BLUETOOTH')

        self.wifi_checkbox.clicked.connect(self.WIFICheckboxClicked)
        self.bluetooth_checkbox.clicked.connect(self.BLUETOOTHCheckboxClicked)
        layout.addRow(self.wifi_checkbox_label, self.wifi_checkbox)
        layout.addRow(self.bluetooth_checkbox_label, self.bluetooth_checkbox)
        # ----------------------------------------



        # YAW SLIDER
        self.yaw_sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.yaw_sld.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.yaw_sld.setFixedWidth(100)
        self.yaw_sld.setMinimum(1)
        self.yaw_sld.setMaximum(200) # maximum angle per press
        # since I did not find way to define float values for the slide bar I consider integer values
        # and divide them by a factor of 10, so when I read the vale from the slide bar a divide by a factor of 10
        # while when I set up the default values of the slide bar I multyuply the sensibility by a factor of 10
        self.yaw_sld.setValue(int(self.parent.yaw_sensibility*10))
        self.yaw_sld.setTickInterval(1)
        self.yaw_sld.setTickPosition(QtGui.QSlider.TicksLeft)

        # YAW SLIDER'S LABEL
        self.yaw_label = QtGui.QLabel(self)
        self.yaw_label.setText('Yaw: ' + str(self.yaw_sld.value()/10))
        # self.velocity_label.setGeometry(640 + self.yaw_sld.width(), self.pbtn.height() + self.btn.height(), 100, 100)
        self.yaw_label.setToolTip('yaw sensibility angle for the robot\'s camera')
        self.yaw_sld.valueChanged[int].connect(self.yawChangeValue)

        layout.addRow(self.yaw_label, self.yaw_sld)

        # PITCH SLIDER
        self.pitch_sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.pitch_sld.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.yaw_sld.setFixedWidth(100)
        self.pitch_sld.setMinimum(1)
        self.pitch_sld.setMaximum(200)  # maximum angle per press
        # since I did not find way to define float values for the slide bar I consider integer values
        # and divide them by a factor of 10, so when I read the vale from the slide bar a divide by a factor of 10
        # while when I set up the default values of the slide bar I multyuply the sensibility by a factor of 10
        self.pitch_sld.setValue(int(self.parent.pitch_sensibility*10))
        self.pitch_sld.setTickInterval(1)
        self.pitch_sld.setTickPosition(QtGui.QSlider.TicksLeft)

        # PITCH SLIDER'S LABEL
        self.pitch_label = QtGui.QLabel(self)
        self.pitch_label.setText('Pitch: ' + str(self.pitch_sld.value()/10))
        # self.velocity_label.setGeometry(640 + self.yaw_sld.width(), self.pbtn.height() + self.btn.height(), 100, 100)
        self.pitch_label.setToolTip('pitch sensibility angle for the robot\'s camera')
        self.pitch_sld.valueChanged[int].connect(self.pitchChangeValue)

        layout.addRow(self.pitch_label, self.pitch_sld)
        # -----------------------------------------------------

        # MAIN WINDOW
        self.setLayout(layout)
        self.setGeometry(300, 300, 300, 300)  # x origin, y origin, width, heght of the window
        self.setWindowIcon(QtGui.QIcon('../img/Settings-L-icon.png'))
        self.setWindowTitle('Settings')

    def WIFICheckboxClicked(self):
        """
        Callback for the wifi checkbox when clicked.
        """
        if self.wifi_checkbox.checkState():
            self.bluetooth_checkbox.setChecked(False)
        else:
            self.bluetooth_checkbox.setChecked(True)

    def BLUETOOTHCheckboxClicked(self):
        """
        Callback for the bluetooth checkbox when clicked.
        """
        if self.bluetooth_checkbox.checkState():
            self.wifi_checkbox.setChecked(False)
        else:
            self.wifi_checkbox.setChecked(True)

    def applyChanges(self):
        """
        Callback of the "Apply "buttons, here we save the parameters inside the GUI class (the parent window)
        """
        self.parent.IP = self.IP_input.text()
        self.parent.min_speed = int(self.min_speed_input.text())
        self.parent.sld.setMinimum(self.parent.min_speed)
        self.parent.timeout = float(self.timeout_input.text())
        self.parent.yaw_sensibility = self.yaw_sensibility
        self.parent.pitch_sensibility = self.pitch_sensibility
        if self.bluetooth_checkbox.checkState():
            self.parent.communication_style = 'BLUETOOTH'
        else:
            self.parent.communication_style = 'WIFI'

        self.close()

    def cancelBtn(self):
        """
        Close the window
        """
        self.close()

    def yawChangeValue(self, value):
        """
        Change value of the speed accordingly to the slidebar
        :param value:
        :return:
        """
        str_ = 'Yaw: ' + str(value/10)
        self.yaw_sensibility = value/10
        self.yaw_label.setText(str_)

    def pitchChangeValue(self, value):
        """
        Change value of the speed accordingly to the slidebar
        :param value:
        :return:
        """
        str_ = 'Pitch: ' + str(value/10)
        self.pitch_sensibility = value/10
        self.pitch_label.setText(str_)
