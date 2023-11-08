from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser



class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model  = CustomUser
		fields = ['phone_number','first_name','last_name','about','avatar']


class CustomUserLoginForm(AuthenticationForm):
	class Meta:
		model  = CustomUser
		fields = ['phone_number',]


class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model  = CustomUser
		fields = ['phone_number','first_name','last_name','about','avatar']