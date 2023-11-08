from django.contrib import admin
from .models import Payment, Visit, Transactions
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
	add_form = CustomUserCreationForm
	form  	 = CustomUserChangeForm
	model 	 = CustomUser

	list_display = ('first_name','last_name','phone_number', 'is_staff', 'is_client',)
	list_filter = ('is_client','is_staff')#('first_name','last_name','phone_number', 'is_staff', 'is_active',)

	fieldsets = (
		(None, {'fields': ('phone_number', 'password')}),
		('Personal info',{'fields':('first_name','last_name', 'about','avatar')}),
		('Permissions', {'fields': ('is_staff', 'is_active','is_client')}),
	)
	add_fieldsets = (
		(None,{
			'classes': ('wide,'), 
			'fields' : ('first_name','last_name','phone_number', 'password1', 'password2', 'is_staff', 'is_active','is_client')
			}
	    ),
	)
	search_fields = ('first_name','last_name','phone_number',)
	ordering = ('first_name','last_name','phone_number',)


admin.site.register(CustomUser, CustomUserAdmin)
# Register your models here.
admin.site.register(Payment)
admin.site.register(Visit)
admin.site.register(Transactions)