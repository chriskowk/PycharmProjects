import ctypes
import win32gui
import win32api
import win32con


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_ulong),
                ('top', ctypes.c_ulong),
                ('right', ctypes.c_ulong),
                ('bottom', ctypes.c_ulong)]

def get_work_area():
  rect = RECT()
  ctypes.windll.user32.SystemParametersInfoA(win32con.SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
  return rect

rect = get_work_area()
print('it worked!')
print(rect.left)
print(rect.top)
print(rect.right)
print(rect.bottom)