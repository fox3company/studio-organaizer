# from django.contrib import admin
# from django.conf import settings
from django.urls import path, include
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views
from .views import StudentLoginView, StudentLogoutView
urlpatterns = [
    path('login/', StudentLoginView.as_view() , name='login'),
    path('logout/', StudentLogoutView.as_view(), name='logout')
    # path('registration/', StudentCreationView.as_view()),
    # path('log_in/', StudentLoginView.as_view()),
    # path('log_out', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
]

