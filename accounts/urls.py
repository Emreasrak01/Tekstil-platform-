
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_choice, name='register_choice'),
    path('register/factory/', views.factory_register, name='factory_register'),
    path('register/store/', views.store_register, name='store_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]