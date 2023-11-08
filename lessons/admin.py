from django.contrib import admin
from .models import Lesson, Studio, Location, ActivityType
from .forms import LessonCreationForm, LessonChangeForm

# Register your models here.
# admin.site.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
  add_form = LessonCreationForm
  form     = LessonChangeForm
  model    = Lesson

  list_display 		  = ['activity','teacher','quantity','get_clients','start_date','start_time','duration','studio']
  empty_value_display = "None"

  fieldsets = (
    ('Genera Info', {'fields': ('activity', 'teacher','quantity','clients')}),
    ('Date&Time',{'fields':('start_date','start_time', 'end_at')}),
    ('Where', {'fields': ('studio',)}),
  )
  # add_fieldsets = (
  #   (None,{
  #     'classes': ('wide,'), 
  #     'fields' : ('first_name','last_name','phone_number', 'password1', 'password2', 'is_staff', 'is_active','is_client')
  #     }
  #     ),
  # )

  def get_clients(self, instance):
    return [f"#{client.phone_number}\n" for client in instance.clients.all()]

admin.site.register(Lesson, LessonAdmin)
admin.site.register(ActivityType)
admin.site.register(Studio)
admin.site.register(Location)
