from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-bin/', views.generate_bin, name='generate_bin'),
    path('generate-image/', views.generate_image, name='generate_image'),
]
