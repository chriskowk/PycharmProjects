import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from queryWeather import Ui_MainWindow
import requests


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def query(self):
        print('* query')
        cityName = self.ui.comboBox.currentText()
        cityCode = self.transCityName(cityName)
        url = 'http://www.weather.com.cn/data/sk/'+cityCode+'.html'
        rep = requests.get(url)
        rep.encoding = 'utf-8'
        #print( rep.json() )
        self.ui.textEdit.setText(str(rep.json()))

    def transCityName(self, cityName):
        cityDic = {'北京':'101010100','天津':'101030100','深圳':'101280601'}
        return cityDic[cityName]

    def clear(self):
        self.ui.textEdit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())