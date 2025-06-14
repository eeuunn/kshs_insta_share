from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_menu, name='test_menu'),
    path('upload/', views.upload_story, name='upload_story'),
]