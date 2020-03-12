from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='checklist-home'),
    path('home/', views.home, name='checklist-home'),
    path('about/', views.about, name='checklist-about'),
]