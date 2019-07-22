from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,FileResponse
from django.urls import reverse
from . import forms
from . import models
from django.template import Context, Template
import re
from datetime import datetime as dt
from datetime import timedelta as td
import hashlib
#from django.views.generic import TemplateView,ListView
from . import send_email_function as send
import threading
import pythoncom
import os

managerlist=['C00075'] #此处设置具有管理员权限的work_id

class content():
    def __init__(self,tag,*args,**kwargs):
        self.tag=tag
        self.inside=[]
        for i in args:
            self.inside.append(i)
        self.tp=self.cal_total_price()
        self.tp2=self.cal_total_price2()
    
    def cal_total_price(self):
        try:
            total_price=0
            for i in self.inside:
                total_price=total_price+i.totalprice
            return total_price
        except:
            return 0
    
    def cal_total_price2(self):
        try:
            total_price=0
            for i in self.inside:
                total_price=total_price+i.tp
            return total_price
        except:
            return 0

def lsum(l):
    s=0
    for i in l:
        s=s+i
    return s

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()
# Create your views here.
def deletecodeintime():
    now=dt.now()
    for obj in models.Change_code.objects.all():
        t=obj.modify_time.replace(tzinfo=None)
        delta=(now-t).total_seconds()
        if delta>=60*5:
            try:
                obj.delete()
            except:
                pass

def gen_datelist(startdatestr,enddatestr):
    [sy,sm,sd]=startdatestr.split('-')
    [ey,em,ed]=enddatestr.split('-')
    startdate=dt(year=int(sy),month=int(sm),day=int(sd))
    enddate=dt(year=int(ey),month=int(em),day=int(ed))
    if startdate>=enddate:
        return [enddate]
    else:
        delta=enddate-startdate
        datelist=[]
        for d in range(delta.days+1):
            datelist.append(enddate-td(days=d))
        return datelist
    
def write_state_file(managewid,widset,dlist):
    date=dt.now()
    y=str(date.year)
    m=str(date.month).zfill(2)
    d=str(date.day).zfill(2)
    h=str(date.hour).zfill(2)
    mi=str(date.minute).zfill(2)
    s=str(date.second).zfill(2)
    datestring='{}-{}-{}_{}-{}-{}'.format(y,m,d,h,mi,s)
    firstline=','
    for day in dlist:
        y=day.year
        m=day.month
        d=day.day
        daystring='{}-{}-{}'.format(y,m,d)
        firstline=firstline+daystring+','
    firstline=firstline+'选定时间内总消费,'
    remaining=''
    all_total=[]
    for i in widset:
        name=models.Person.objects.get(work_id=i)
        newline=i+'（{}）'.format(name)+','
        person_total=[]
        for day in dlist:
            y=day.year
            m=day.month
            d=day.day
            order_list=models.Order_relation.objects.all().filter(order_date__year=y,\
                    order_date__month=m,order_date__day=d,person__work_id=i)
            grid=''
            daytotal=0
            for e in order_list:
                daytotal=daytotal+e.totalprice
                grid=grid+e.food.name+' X '+str(e.quantity)+'；'
            person_total.append(daytotal)
            grid=grid+'当日总价：'+str(daytotal)
            newline=newline+grid+','
        remaining=remaining+newline+str(lsum(person_total))+'\n'
        all_total.append(lsum(person_total)) #将每个人在此时间内的总消费分别记录到这个list中
    allcontent='总消费：'+str(lsum(all_total))+'元'+',\n'+firstline+'\n'+remaining
    if os.path.exists('state_repository\\{0}'.format(managewid)):
        with open('state_repository\\{0}\\{0}_request_{1}.csv'.format(managewid,datestring),'w') as f:
            f.write(allcontent)
    else:
        os.mkdir('state_repository\\{0}'.format(managewid))
        with open('state_repository\\{0}\\{0}_request_{1}.csv'.format(managewid,datestring),'w') as f:
            f.write(allcontent)
    if os.path.exists('state_repository\\newest_state'):
        with open('state_repository\\newest_state\\{0}.csv'.format(managewid),'w') as f:
            f.write(allcontent)
    else:
        os.mkdir('state_repository\\newest_state'.format(managewid))
        with open('state_repository\\newest_state\\{0}.csv'.format(managewid),'w') as f:
            f.write(allcontent)
    
            
        
A_signup=r'''<br/><a href="{% url 'menus:sign_up' %}">点击返回</a>'''
A_login=r'''<br/><a href="{% url 'menus:login' %}">点击返回</a>'''
A_menus=r'''<a href="{% url 'menus:menus' %}">点击返回</a>'''
A_personal=r'''<a href="{% url 'menus:personalhome' %}">点击查看订餐记录</a>'''
A_manage=r'''<a href="{% url 'menus:manage' %}">返回管理员页面</a>'''

def home(request):
    if 'login' in request.session and request.session['login']==True:
        MAP={'wid':request.session['work_id'],
             'name':request.session['name']}
        return render(request,'menus/welcome.html',MAP)
#        return HttpResponseRedirect(reverse('menus:menus'))
    else:
        return HttpResponseRedirect(reverse('menus:login'))

def login(request):
    if request.method=="POST":
        login_form=forms.Login(request.POST)
        if login_form.is_valid():
            work_id=login_form.cleaned_data['work_id']
            password=login_form.cleaned_data['password1']
            try:
                user=models.Person.objects.get(work_id=work_id)
                if user.password==hash_code(password):
                    request.session['login']=True
                    request.session['work_id']=user.work_id
                    request.session['name']=user.name
                    request.session.set_expiry(60*30) #设置session过期时间
                    return HttpResponseRedirect(reverse('menus:home'))
                else:
                    return HttpResponse('密码错误')
            except:
                return HttpResponse('用户不存在')
        return HttpResponse('输入内容不能为空')
    else:
        return render(request,'menus/login.html',{})
        

def sign_up(request):
    if request.method=="POST":
        signup_form=forms.Sign_in(request.POST)
        if signup_form.is_valid():
            name=signup_form.cleaned_data['name'] #！！此处最好给name加上一个匹配汉字的正则表达式
            work_id=signup_form.cleaned_data['work_id']
            em=signup_form.cleaned_data['email']
            password1=signup_form.cleaned_data['password1']
            password2=signup_form.cleaned_data['password2']
            if password1==password2 and re.match(r'^C\d\d\d\d\d$',work_id):
                try:
                    user=models.Person(name=name,work_id=work_id,\
                                       email=em,password=hash_code(password2))
                    user.save()
                    tp=Template('注册成功'+A_menus)
                    c=Context({})
                    return HttpResponse(tp.render(c))
                except:
                    tp=Template('''创建用户过程中出现了错误,最有可能是出现了重复的work_id'''\
                                 +A_signup)
                    c=Context({})
                    return HttpResponse(tp.render(c))
            else:
                tp=Template('输入的work id不符合要求或两次输入密码不一致'+A_signup)
                c=Context({})
                return HttpResponse(tp.render(c))
        else:
            return render(request,'menus/sign_up.html',{})
        
    else:
        return render(request,'menus/sign_up.html',{})

def menus(request):
    if 'login' in request.session and request.session['login']==True:
        Food_list=models.Food.objects.filter(active=True)
        wid=request.session['work_id']
        name=request.session['name']
        filter_id=models.Order_relation.objects.all().filter(person__work_id__exact=wid)
        date=dt.now()
        y=date.year
        m=date.month
        d=date.day
        order_list=filter_id.filter(order_date__year=y,order_date__month=m,order_date__day=d)
        total_price=0
        for item in order_list:
            total_price=total_price+item.totalprice
        MAP={'Food_list':Food_list,
             'wid':wid,
             'name':name,
             'order_list':order_list,
             'total_price':total_price}
        return render(request,'menus/menus.html',MAP)
    else:
        return HttpResponseRedirect(reverse('menus:login'))

def personalhome(request):
    if 'login' in request.session and request.session['login']==True:
        wid=request.session['work_id']
        if request.method=="GET":
            date=dt.now()
            y=str(date.year)
            m=str(date.month).zfill(2)
            d=str(date.day).zfill(2)
            datestring='{}-{}-{}'.format(y,m,d)
            order_list=models.Order_relation.objects.all().filter(order_date__year=y,\
                    order_date__month=m,order_date__day=d,person__work_id=wid)
            MAP={'order_list':order_list,
                 'date_time':datestring,
                 'wid':wid,
                 'name':request.session['name']}
            return render(request,'menus/personalhome.html',MAP)
        elif request.method=="POST":
            datestring=request.POST['selectdate']
            st=request.POST['selectdate'].split('-')
            sy=st[0]
            sm=st[1]
            sd=st[2]
            order_list=models.Order_relation.objects.all().filter(order_date__year=sy,\
                    order_date__month=sm,order_date__day=sd,person__work_id=wid)
            MAP={'order_list':order_list,
                 'date_time':datestring,
                  'wid':wid,
                 'name':request.session['name']}
            return render(request,'menus/personalhome.html',MAP)
    else:
        return HttpResponseRedirect(reverse('menus:login'))
        
    return HttpResponse('welcome into your personal page')

    
def manage(request):
    global managerlist
    if ('login' in request.session) and (request.session['login'] \
           ==True) and (request.session['work_id'] in managerlist):
        wid=request.session['work_id']
        name=request.session['name']
        date=dt.now()
        y=str(date.year)
        m=str(date.month).zfill(2)
        d=str(date.day).zfill(2)
        date_time=['{}-{}-{}'.format(y,m,d)]
        if request.method=='GET':  
            context={'download':'',
                     'wid':wid,
                     'name':name,
                     'date_time1':date_time[0],
                     'date_time2':date_time[0],
                    'personlist':models.Person.objects.all(),
                     'datelist':date_time, 
                     'flag':False}
            return render(request,'menus/manage.html',context)
        if request.method=='POST':
            ##confirm datelist start
            dlist=gen_datelist(request.POST['startdate'],request.POST['enddate'])
            date_time=[]
            for date in dlist:
                y=str(date.year)
                m=str(date.month).zfill(2)
                d=str(date.day).zfill(2)
                date_time.append('{}-{}-{}'.format(y,m,d))
            date_time.reverse()
            widlist=request.POST.getlist('selectedperson')
#            selectpersonlist=[]
            relationcontent=content('outside') #最外层
            dlist.reverse()
            for i in widlist:
                temp=content(i)
                 #person层,temp为每个person信息
                for date in dlist:
                    y=date.year
                    m=date.month
                    d=date.day
#                    datestr='{}{}{}'.format(str(y),str(m).zfill(2),str(d).zfill(2))
                    objlist=models.Order_relation.objects.filter(person__work_id=i,\
                            order_date__year=y,order_date__month=m,order_date__day=d)
                    temp2=content(date,*objlist) #这个人在dlist中某一天所点
                    temp.inside.append(temp2) #将这个人在dlist中所有天所点添加入temp.inside中
                relationcontent.inside.append(temp) #将这个人的所有点餐信息包含进relationcontent中
            ##confirm datelist end
            context={'download':'''<a href='download'>下载统计表</a>''',
                     'wid':wid,
                     'name':name,
                     'date_time1':request.POST['startdate'],
                     'date_time2':request.POST['enddate'],
                     'personlist':models.Person.objects.all(),
                     'widlist':widlist,
                     'datelist':date_time, 
                     'relationcontent':relationcontent}
#            try:
            write_state_file(wid,widlist,dlist)
            return render(request,'menus/manage.html',context)
#            except:
#                tp=Template('写文件失败  '+A_manage)
#                c=Context({})
#                return HttpResponse(tp.render(c))  
#            return HttpResponse(str(relationcontent))
    else:
        tp=Template('''您未登陆或您不是管理员 '''\
                                 +A_login)
        c=Context({})
        return HttpResponse(tp.render(c))
        
#    return HttpResponse('dear manager')
def manage_menus(request):
    global managerlist
    if ('login' in request.session) and (request.session['login'] \
           ==True) and (request.session['work_id'] in managerlist):
#        Food_list=models.Food.objects.all()
        Food_active=models.Food.objects.filter(active=True)
        Food_frozen=models.Food.objects.filter(active=False)
        wid=request.session['work_id']
        name=request.session['name']
        if request.method=="GET":
            context={'Food_active':Food_active,
             'Food_frozen':Food_frozen,
             'wid':wid,
             'name':name}
            return render(request,'menus/manage_menus.html',context)
        elif request.method=="POST":
             #在页面模板上使用js设置，某一个菜品如果某一属性被改变，则其在html-form中的
             #某个flag被改变。
             #最后此视图通过识别被改变的flag实现仅对发生修改的菜品的数据库
             #条目进行修改。
            context={'Food_active':Food_active,
             'Food_frozen':Food_frozen,
             'wid':wid,
             'name':name}
            return render(request,'menus/manage_menus.html',context)       
    else:
        tp=Template('''您未登陆或您不是管理员 '''\
                                 +A_login)
        c=Context({})
        return HttpResponse(tp.render(c))

def download(request):
    if 'work_id' in request.session and request.session['work_id'] in managerlist:
        manageid=request.session['work_id']
        try:
            return FileResponse(open('state_repository\\newest_state\\{}.csv'.format(manageid),'rb'),as_attachment=True)
        except:
            tp=Template('''文件不存在，请重新请求 '''+A_manage)
            c=Context({})
            return HttpResponse(tp.render(c))
    else:
        tp=Template('''您未登录或您不是管理员,请登录 '''+A_login)
        c=Context({})
        return HttpResponse(tp.render(c))

def logoff(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('menus:login'))

def finished(request):
    if dt.now().hour<24:
        if 'login' in request.session and request.session['login']==True:
            wid=request.session['work_id']
            p=models.Person.objects.get(work_id=wid)
            if request.method=="POST":
                keylist=[]
#                orderlist=[]
                for key in request.POST.keys():
                    keylist.append(key)
#                    orderlist.append(request.POST[key])
#                    orderlist.append(request.POST[key]  )
#                return HttpResponse('预定完毕')
                finishstr='''
                    <h1>预定完毕，您预定的内容如下</h1>
                    <br/>
                    <hr/>
                '''
                posttime=dt.now()
                clearitem=models.Order_relation.objects.all().filter(\
                        person=p,order_date__year=posttime.year,\
                            order_date__month=posttime.month,\
                            order_date__day=posttime.day)
                clearitem.delete()
                keypack=[]
                i=0 #定义一个奇偶计数器
                for key in keylist[1:]:
                    if i%2==0: #如果i是偶数
                        pack=[]
                        pack.append(key)
                        i=i+1
                    else:
                        pack.append(key)
                        keypack.append(pack)
                        i=i+1
                        
                for key in keypack:
                    pkt=re.match(r'\d*',key[0]).group()
                    f=models.Food.objects.get(pk=pkt)
                    q=int(request.POST[key[0]])
                    req=request.POST[key[1]]
                    orr=models.Order_relation(person=p,food=f,quantity=q,\
                                              requirement=req,\
                                              order_date=dt.now())
                    orr.save()
                    finishstr=finishstr+r'<li>{} × {} 要求：{}</li><br/>'.format(f.name,q,req)

#                return HttpResponse(finishstr)
                tp=Template(finishstr+A_personal)
                c=Context({})
                return HttpResponse(tp.render(c))  
            else:
                return HttpResponseRedirect(reverse('menus:menus'))
        else:
            return HttpResponseRedirect(reverse('menus:login'))
    else:
        tp=Template('''订餐失败，超过订餐时间，订餐已经结束。 '''\
                                 +A_menus)
        c=Context({})
        return HttpResponse(tp.render(c))
    
def changepassword1(request):
    if request.method=='POST':
        emaddr=request.POST['email']
        wid=request.POST['work_id']
        try:
            models.Person.objects.get(work_id=wid,email=emaddr)
        except:
            tp=Template('没有匹配的用户和邮箱'+A_login)
            c=Context({})
            return HttpResponse(tp.render(c))
        else:
            code=send.gen_random()
            cc=models.Change_code(verify=code,email=emaddr,work_id=wid)
            cc.save()
            try:
                pythoncom.CoInitialize()
                send.sendmail(emaddr,code)
            except:
                tp=Template('邮件发送失败'+A_login)
                c=Context({})
                return HttpResponse(tp.render(c))
            thread=threading.Thread(target=deletecodeintime,args=(cc))
            thread.start() #启动计时删除程序
            tp=Template('邮件发送成功，请查收'+A_login)
            c=Context({})
            return HttpResponse(tp.render(c))
    else:
        return render(request,"menus/changepassword.html",{})
#        pass



def changepassword2(request,code):
    deletecodeintime()
    try:
        cc=models.Change_code.objects.get(verify=code)
    except:
        tp=Template('链接不存在'+A_login)
        c=Context({})
        return HttpResponse(tp.render(c))
    else:
        if request.method=="POST":
            wid=cc.work_id
            p=models.Person.objects.get(work_id=wid)
            if request.POST['password1']==request.POST['password2']:
                p.password=hash_code(request.POST['password2'])
                p.save()
                tp=Template('密码修改成功'+A_login)
                c=Context({})
                cc.delete()
                return HttpResponse(tp.render(c))
            else:
                tp=Template('两次输入密码不一致'+A_login)
                c=Context({})
                return HttpResponse(tp.render(c))
        else:
            return render(request,"menus/changepassword2.html",{'code':cc.verify})

#########################################
#############test class view#############
#########################################     

    
    
    
    