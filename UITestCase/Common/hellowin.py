import sys
import resources_rc
from PyQt5 import QtWidgets
from PyQt5 import QtGui

app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QWidget()
widget.resize(360, 360)
widget.setWindowTitle("hello, pyqt5")
widget.setWindowIcon(QtGui.QIcon(':/images/image.ico'))
widget.show()
sys.exit(app.exec())