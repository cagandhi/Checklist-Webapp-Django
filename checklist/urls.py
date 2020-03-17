from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='checklist-home'),
    path('about/', views.about, name='checklist-about'),
    path('mychecklist/', views.mychecklist, name='checklist-mychecklist')
]