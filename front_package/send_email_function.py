import win32com.client as win32
import warnings
#import sys
import pythoncom
 
#reload(sys)
#sys.setdefaultencoding('utf8')
warnings.filterwarnings('ignore')
pythoncom.CoInitialize()
def sendmail(recv,code):
    sub = '点餐系统密码修改'
    body = r'''请点击此链接修改密码：
                127.0.0.1/{}
                '''.format(code)
    outlook = win32.Dispatch('outlook.application')
    receivers = [recv]
    mail = outlook.CreateItem(0)
    mail.To = receivers[0]
    mail.Subject = sub
    mail.Body = body
#    mail.Attachments.Add('C:\Users\xxx\Desktop\git_auto_pull_new.py')
    mail.Send()
 
#recv='751752563@qq.com'
#code='123456'
#sendmail(recv,code)