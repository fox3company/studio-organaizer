from django.contrib import admin
from .models import Lesson, Studio, Location, ActivityType, Client, CTransactions, Student

# Register your models here.
admin.site.register(Lesson)
admin.site.register(ActivityType)
admin.site.register(Studio)
admin.site.register(Location)
admin.site.register(Student)
admin.site.register(Client)
admin.site.register(CTransactions)
