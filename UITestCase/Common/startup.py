import os
import stat

print ('hello python')
os.chmod( '测试只读属性.txt', stat.S_IWRITE )
