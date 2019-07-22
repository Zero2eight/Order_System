import win32com.client as win32
import warnings
#import sys
import pythoncom
import random
 
#reload(sys)
#sys.setdefaultencoding('utf8')
warnings.filterwarnings('ignore')
pythoncom.CoInitialize()
def sendmail(recv,code):
    sub = '点餐系统密码修改'
    body = r'''请点击此链接修改密码：
                http://127.0.0.1:8000/menus/changepassword2/{}
                请在5分钟内修改密码，否则链接将失效
                '''.format(code)
    outlook = win32.Dispatch('outlook.application')
    receivers = [recv]
    mail = outlook.CreateItem(0)
    mail.To = receivers[0]
    mail.Subject = sub
    mail.Body = body
#    mail.Attachments.Add('C:\Users\xxx\Desktop\git_auto_pull_new.py')
    mail.Send()

def gen_random():
    i=6
    content=[]
    while i>0: 
        r=random.randint(0,9)
        content.append(r)
        i=i-1
    codestr=''
    for e in content:
        codestr=codestr+str(e)
    return codestr
    

#recv='751752563@qq.com'
#code='123456'
#sendmail(recv,code)