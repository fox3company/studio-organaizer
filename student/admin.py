from django.contrib import admin
from .models import Lesson, Studio, Location

# Register your models here.
admin.site.register(Lesson)
admin.site.register(Studio)
admin.site.register(Location)