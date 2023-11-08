from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .views import LessonsListView, ActivityTypesListView, LocationsStudiosListView, LocationLessonsListView
from django.utils import timezone

now  = timezone.now().isocalendar()
week = now.week
year = now.year

urlpatterns = [
    path('', LessonsListView.as_view(), {'year': year,'week': week}, name="now_week_lessons"),
    path('<int:year>/<int:week>/', LessonsListView.as_view(), name="n_week_lessons"),
    path('<int:year>/<int:week>/<str:location>/', LocationLessonsListView.as_view(), name="location_n_week_lessons"),
    path('activity_types/', ActivityTypesListView.as_view(), name="activity_types"),
    path('studios/', LocationsStudiosListView.as_view(), name="studios")
    # path('', TemplateView.as_view(template_name="student/index.html")),
]
