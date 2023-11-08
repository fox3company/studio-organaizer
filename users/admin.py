from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Student, Client, Teacher


class CustomUserAdmin(UserAdmin):
	add_form = CustomUserCreationForm
	form  	 = CustomUserChangeForm
	model 	 = CustomUser

	list_display = ('first_name','last_name','phone_number', 'is_staff', 'is_client','is_teacher')
	list_filter = ('is_client','is_staff','is_teacher')#('first_name','last_name','phone_number', 'is_staff', 'is_active',)

	fieldsets = (
		(None, {'fields': ('phone_number', 'password')}),
		('Personal info',{'fields':('first_name','last_name', 'about','avatar')}),
		('Permissions', {'fields': ('is_staff', 'is_active','is_client','is_teacher')}),
	)
	add_fieldsets = (
		(None,{
			'classes': ('wide,'), 
			'fields' : ('first_name','last_name','phone_number', 'password1', 'password2', 'is_staff', 'is_active','is_client','is_teacher')
			}
	    ),
	)
	search_fields = ('first_name','last_name','phone_number',)
	ordering = ('first_name','last_name','phone_number',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Client)
admin.site.register(Teacher)
# Register your models here.
