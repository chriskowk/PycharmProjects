import smtplib
import time
import xlrd
from email import encoders
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.application import MIMEApplication
from datetime import date, datetime

sender = '244587466@qq.com'
receiver = 'chriskwok@126.com'

def read_excel():
    # 打开Excel文件
    # 读取群发邮箱，将需要群发的邮箱复制到test的excel列表清单中
    excelFileUrl = xlrd.open_workbook(r'F:\GitHub\PycharmProjects\PyQtTest\data\email_list.xlsx')
    print(excelFileUrl.sheet_names())
    # 获取第一个sheet页面
    sheet1 = excelFileUrl.sheet_by_index(0)
    print(sheet1.name, sheet1.nrows, sheet1.ncols)
    # 获取第2列的邮箱列表
    email_data = sheet1.col_values(0)
    print(email_data)
    return email_data

def sender_mail():
    # 创建对象
    smt_p = smtplib.SMTP()
    # 设置smtp服务器
    smt_p.connect(host='smtp.qq.com', port=25)
    # 在qq邮箱设置开启SMTP服务并复制授权码
    password = "djachxbcdtfwcaef"
    # 进行邮箱登录一次，填写你本人的邮箱
    smt_p.login(sender, password)
    count_num = 1
    # 使用for循环来进行发邮件
    for i in read_excel():
        # 表格中邮箱格式不正确，如有空字符，在发邮件的时候会出现异常报错，捕获到这些异常就跳过
        try:
            # 邮件设置
            msg = MIMEMultipart()
            msg['From'] = "CHRIS KWOK"
            # 收件人
            msg['To'] = i
            msg['Cc'] = receiver
            # 主题名称
            msg['subject'] = Header('通知', 'utf-8')
            # 附件 —附加发送excel、word、图片格式，新建文件夹，将以下路径及文件名称替换即可。
            msg.attach(MIMEText('您好,' 'XXX2.0全新升级，XXX1.0版本到2018年10月31号停止所有服务。', 'plain', 'utf-8'))
            xlsxpart = MIMEApplication(open(r'F:\GitHub\PycharmProjects\PyQtTest\data\email_test.xlsx', 'rb').read())
            xlsxpart.add_header('Content-Disposition', 'attachment', filename='1.xlsx')
            msg.attach(xlsxpart)
            message_docx1 = MIMEText(open(r'F:\GitHub\PycharmProjects\PyQtTest\data\email_test.docx', 'rb').read(), 'base64', 'utf8')
            message_docx1.add_header('content-disposition', 'attachment', filename='测试.docx')
            msg.attach(message_docx1)
            message_image = MIMEText(open(r'F:\GitHub\PycharmProjects\PyQtTest\data\email_test.jpg', 'rb').read(), 'base64', 'utf8')
            message_image.add_header('content-disposition', 'attachment', filename='plot2.jpg')
            msg.attach(message_image)
            # 发送邮件
            smt_p.sendmail(sender, i, msg.as_string())
            # sleep10秒避免发送频率过快，可能被判定垃圾邮件。
            time.sleep(10)
            print('第%d次发送给%s' % (count_num, i))
            count_num = count_num + 1
        except (UnicodeEncodeError, smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused, AttributeError) as e:
            # 打印出来发送第几次的时候，邮箱出问题，一个邮箱最多不超过300个发送对象
            print('第%d次给%s发送邮件异常' % (count_num, i))
            continue
    smt_p.quit()

sender_mail()

