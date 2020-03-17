from django.urls import path
from . import views
from .views import ChecklistListView, ChecklistDetailView

urlpatterns = [
    path('', ChecklistListView.as_view(), name='checklist-home'), #path('', views.home, name='checklist-home'),
    path('checklist/<int:pk>/', ChecklistDetailView.as_view(), name='checklist-detail'),
    path('about/', views.about, name='checklist-about'),
    path('mychecklist/', views.mychecklist, name='checklist-mychecklist')
]