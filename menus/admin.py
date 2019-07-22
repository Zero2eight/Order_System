from django.contrib import admin

from .models import Person,Restaurant,Food,Order_relation,Change_code

admin.site.register(Person)
admin.site.register(Restaurant)
admin.site.register(Food)
#admin.site.register(Order_relation)
admin.site.register(Change_code)
# Register your models here.
