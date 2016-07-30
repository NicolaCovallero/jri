"""
SettingsWindow

Windows for the settings of the GUI
"""

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

        # MAIN WINDOW
        self.setLayout(layout)
        self.setGeometry(300, 300, 300, 300) # x origin, y origin, width, heght of the window
        self.setWindowIcon(QtGui.QIcon('img/Settings-L-icon.png'))
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

