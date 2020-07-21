import sys
from PyQt5 import QtGui, QtCore, QtWidgets

class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.le = QtWidgets.QLineEdit()
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.le)
        self.le.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())
            # do something
        return QtWidgets.QWidget.eventFilter(self, watched, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
