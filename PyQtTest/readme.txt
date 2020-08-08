pyrcc5 -o resources_rc.py resources_rc.qrc
pyinstaller.exe --hidden-import=PyQt5 -F -w -i images\scheduler.ico trayicondemo.py

打包 PyQt5 项目：
1. 打包命令：pyinstaller.exe --hidden-import=PyQt5 -F -w -i images\scheduler.ico trayicondemo.py
命令参数说明：
-F, –onefile 打包成一个exe文件。-D, –onedir 创建一个目录，包含exe文件，但会依赖很多文件（默认选项）。
-c, –console, –nowindowed 使用控制台，无界面(默认)-w, –windowed, –noconsole 使用窗口，无控制台--hidden-import= PyQt5  导入PyQt模块
2. 添加窗口图标：
(1). 新建一个resources_rc.qrc文本，写入下面内容：
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource prefix="/images">
        <file alias="image.ico">images/image.ico</file>
    </qresource>
</RCC>
(2). 转换qrc为py格式，执行命令生成py文件：
pyrcc5 -o resources_rc.py resources_rc.qrc
(3). 导入py文件到程序中
import resources_rc
MainWindow.setWindowIcon(QtGui.QIcon(':/images/image.ico'))
指定打包后即可看到任务栏图标会变成你自定义的图标
