from django.urls import path,include

from . import views
app_name='menus'
urlpatterns=[
        path('',views.home,name='home'),
        path('sign_up',views.sign_up,name='sign_up'),
        path('login',views.login,name='login'),
        path('menus',views.menus,name='menus'),
        path('personalhome',views.personalhome,name='personalhome'),
        path('manage',views.manage,name='manage'),
        path('manage_menus',views.manage_menus,name='manage_menus'),
        path('logoff',views.logoff,name='logoff'),
        path('finished',views.finished,name="finished"),
        path('changepassword',views.changepassword1,name="changepassword"),
        path('changepassword2/<code>/',views.changepassword2,name="changepassword2"),
        path('download',views.download,name='download')]