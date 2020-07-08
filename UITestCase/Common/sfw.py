import os
import stat
import sys
import argparse

def main():
    if len(sys.argv) < 2:
        print("Usage: sfw.exe <path> [--quiet]")
        print("Purpose: Remove file's READONLY attribute recursively descend the directory tree rooted at <path>.")
        print("PS: 如目标路径存在空格需用双引号括起来！")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="功能：递归清除<path>指定路径所有文件的只读属性")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 版本: V1.0', help='显示程序版本')
    parser.add_argument('-d', '--debug', action='store_true', help='设置为调试模式运行', default=False)
    parser.add_argument('-q', '--quiet', action='store_true', help='显示每个对象操作结果', default=False)
    parser.add_argument("path", type=str, help='指定目标文件路径')
    args = parser.parse_args()
    path_ = args.path
    debug_=args.debug
    quiet_=args.quiet
    # print('the path is %s'%(path_))
    # print('the quiet on is %s'%(quiet_))

    filelist = [os.path.join(path, file_name)
        for path, _, file_list in os.walk(path_)
        for file_name in file_list]
    for fn in filelist:
        os.chmod(fn, stat.S_IWRITE | stat.S_IRWXU)
        if not quiet_:
            print("文件 {} 只读属性已清除".format(fn[len(path_):]))
    sys.exit(0)

# CMD窗口编译 D:\PycharmProjects\UITestCase\Common>pyinstaller --console --onefile --icon=file.ico sfw.py
# flags:可用以下选项按位或操作生成， 目录的读权限表示可以获取目录里文件名列表，执行权限表示可以把工作目录切换到此目录，
# 删除添加目录里的文件必须同时有写和执行权限，文件权限以用户id->组id->其它顺序检验,最先匹配的允许或禁止权限被应用。
# stat.S_IXOTH: 其他用户有执行权0o001
# stat.S_IWOTH: 其他用户有写权限0o002
# stat.S_IROTH: 其他用户有读权限0o004
# stat.S_IRWXO: 其他用户有全部权限(权限掩码)0o007
# stat.S_IXGRP: 组用户有执行权限0o010
# stat.S_IWGRP: 组用户有写权限0o020
# stat.S_IRGRP: 组用户有读权限0o040
# stat.S_IRWXG: 组用户有全部权限(权限掩码)0o070
# stat.S_IXUSR: 拥有者具有执行权限0o100
# stat.S_IWUSR: 拥有者具有写权限0o200
# stat.S_IRUSR: 拥有者具有读权限0o400
# stat.S_IRWXU: 拥有者有全部权限(权限掩码)0o700
# stat.S_ISVTX: 目录里文件目录只有拥有者才可删除更改0o1000
# stat.S_ISGID: 执行此文件其进程有效组为文件所在组0o2000
# stat.S_ISUID: 执行此文件其进程有效用户为文件所有者0o4000
# stat.S_IREAD: windows下设为只读
# stat.S_IWRITE: windows下取消只读


if __name__ == '__main__':
    main()