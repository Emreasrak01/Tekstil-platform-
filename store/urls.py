from django.urls import path

from . import views


urlpatterns = [
    path('dashboard/', views.store_dashboard, name='store_dashboard'),
    path('orders/', views.store_orders, name='store_orders'),
    path('favorites/', views.store_favorites, name='store_favorites'),
    path('settings/', views.store_settings, name='store_settings'),
    path('cart/', views.store_cart, name='store_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_qty, name='update_cart_qty'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/remove/<int:product_id>/', views.remove_favorite, name='remove_favorite'),
]
