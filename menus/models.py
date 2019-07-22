from django.db import models
from datetime import datetime
# Create your models here.
class Person(models.Model):
    name=models.CharField(max_length=20)
    work_id=models.CharField(max_length=20,unique=True)
    password=models.CharField(max_length=1000)
    register_time=models.DateTimeField(auto_now_add=True)
    email=models.CharField(max_length=100)
    def __str__(self):
        return self.name

    
class Restaurant(models.Model):
    name=models.CharField(max_length=50)
    addrs=models.CharField(max_length=100,blank=True)
    tel=models.CharField(max_length=15,blank=True)
    description=models.CharField(max_length=260,blank=True)
    def __str__(self):
        return self.name

class Food(models.Model):
    name=models.CharField(max_length=50)
    price=models.FloatField()
    description=models.CharField(max_length=260,blank=True)
    active=models.BooleanField(default=True)
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    orderby=models.ManyToManyField(Person,through='Order_relation')
    def __str__(self):
        return self.name

class Order_relation(models.Model):
    person=models.ForeignKey(Person,on_delete=models.CASCADE)
    food=models.ForeignKey(Food,on_delete=models.CASCADE)
    requirement=models.CharField(max_length=100,blank=True)
    quantity=models.IntegerField(default=0)
    totalprice=models.FloatField(default=0)
    order_date=models.DateTimeField(auto_now_add=True)
    #要合并同一天同个人点的同种食物，需重新实现save函数
    def delete(self):
        super().delete()
        with open(r'C:\Users\c00075\.spyder-py3\ORDER\menus\delete_log.txt','w') as f:
            contents=f.read()
            contents.append("delete")   
            f.write(contents)
        
    def save(self):
#        super().save()
        t=datetime.now()
        target=Order_relation.objects.all().filter(person__work_id=self.person.work_id,\
                food__pk=self.food.pk,order_date__year=t.year,\
                order_date__month=t.month,\
                order_date__day=t.day)  #筛选出此类型数据
        if  len(target)==0: #如果没有此类型条目，创建新条目并自动初始化其总价
            if self.quantity!=0:
                self.totalprice=self.quantity*self.food.price
                super().save()
        else: #如果有此类型条目，修改此条目
#            print(r'target[0].quantity is ',target[0].quantity)
#            print(r'self.quantity is ',self.quantity)
            target[0].quantity=self.quantity
            if target[0].quantity==0:
                target[0].delete()
            else:
                target[0].totalprice=target[0].quantity*target[0].food.price
                target[0].order_date=datetime.now()
                super(Order_relation,target[0]).save()

class Change_code(models.Model):
    verify=models.CharField(max_length=10)
    email=models.CharField(max_length=100)
    work_id=models.CharField(max_length=20)
    modify_time=models.DateTimeField(auto_now_add=True)
        
        
        
            
            
    
    
    
    