# from django.contrib import admin
# from django.conf import settings
from django.urls import path, include
# from django.views.generic import TemplateView
# from django.contrib.auth import views as auth_views
from .views import StudentLoginView, StudentLogoutView, ProfileView, RegistrationsView, PaymentsListView
from django.utils import timezone

now   = timezone.now()
week  = now.isocalendar().week
month = now.month
year  = now.isocalendar().year

urlpatterns = [
    path('login/', StudentLoginView.as_view() , name='login'),
    path('logout/', StudentLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('registrations/', RegistrationsView.as_view(), {'year': year,'month': month}, name="registrations"),
    path('registrations/<int:year>/<int:month>/', RegistrationsView.as_view(), name='registrations_year_month'),
    path('payments/', PaymentsListView.as_view(), {'year': year}, name="payments"),
    path('payments/<int:year>/', PaymentsListView.as_view(), name='payments_n_year'),
    # path('teachers/', TeachersListView.as_view(), name="teachers_list" ) it's been written directly in the root urls
    # path('registration/', StudentCreationView.as_view()),
    # path('log_in/', StudentLoginView.as_view()),
    # path('log_out', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
]

