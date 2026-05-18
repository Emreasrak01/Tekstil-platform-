# factory/urls.py (yeni dosya oluşturun)
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.factory_dashboard, name='factory_dashboard'),
    path('orders/', views.factory_orders, name='factory_orders'),
    path('reports/', views.factory_reports, name='factory_reports'),
    path('settings/', views.factory_settings, name='factory_settings'),
]