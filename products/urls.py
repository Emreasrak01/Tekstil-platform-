from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='product_home'),

    # Ürün işlemleri
    path('add/', views.add_product, name='add_product'),
    path('list/', views.product_list, name='product_list'),
    path('edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
