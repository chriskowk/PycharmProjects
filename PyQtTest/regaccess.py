from win32api import *
from win32con import *
import os

def get_values(fullname):
    name = str.split(fullname, '\\', 1)
    try:
        if name[0] == 'HKEY_LOCAL_MACHINE':
            key = RegOpenKey(HKEY_LOCAL_MACHINE, name[1], 0, KEY_READ)
        elif name[0] == 'HKEY_CURRENT_USER':
            key = RegOpenKey(HKEY_CURRENT_USER, name[1], 0, KEY_READ)
        elif name[0] == 'HKEY_CLASSES_ROOT':
            key = RegOpenKey(HKEY_CLASSES_ROOT, name[1], 0, KEY_READ)
        elif name[0] == 'HKEY_CURRENT_CONFIG':
            key = RegOpenKey(HKEY_CURRENT_CONFIG, name[1], 0, KEY_READ)
        elif name[0] == 'HKEY_USERS':
            key = RegOpenKey(HKEY_USERS, name[1], 0, KEY_READ)
        else:
            raise ValueError('Error,no key named', name[0])
        info = RegQueryInfoKey(key)
        for i in range(0, info[1]):
            valuename = RegEnumValue(key, i)
            print(str.ljust(valuename[0], 20), valuename[1])
        RegCloseKey(key)
    except Exception as e:
        print('Sth is wrong')
        print(e)


if __name__ == '__main__':
    keyNames = ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run']
    for keyName in keyNames:
        print('*'*30)
        print(keyName)
        get_values(keyName)

    name = 'wep'
    path = "C:\\swe.exe"
    # 注册表项名
    keyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    # 异常处理
    try:
        key = RegOpenKey(HKEY_LOCAL_MACHINE, keyName, 0, KEY_ALL_ACCESS)
        RegSetValueEx(key, name, 0, REG_SZ, path)
        RegCloseKey(key)
    except (OSError, TypeError) as reason:
        print('错误的原因是:', str(reason))
    print(os.path.realpath(__file__))
    print(os.path.split(os.path.realpath(__file__))[0])
