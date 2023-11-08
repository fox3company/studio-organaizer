from django.shortcuts import render
from django.contrib.auth import views as auth_views
# from .forms import StudenLoginForm, StudentCreationForm
# from .model import StudentCreationForm
from django.views.generic import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin

# class StudentLoginView(auth_views.LoginView):
# 	# form_class = 
# 	form_class = StudenLoginForm
#  #    authentication_form = None
#  #    next_page = None
#  #    redirect_field_name = REDIRECT_FIELD_NAME
# 	template_name = "student/registration/login_student.html"
#  #    redirect_authenticated_user = False
#  #    extra_context = None


# class StudentCreationView(CreateView):
# 	template_name = "student/registration/registration_student.html"
# 	form_class    = StudentCreationForm