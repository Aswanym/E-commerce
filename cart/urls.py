from django.urls import path
from .import views


urlpatterns = [

    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>', views.add_cart, name='add_cart'),
    path('add_cart_ajax',views.add_cart_ajax,name="add_cart_ajax"),
    path('minus_cart', views.minus_cart, name='minus_cart'),
    path('delete_cart', views.delete_cart, name='delete_cart'),

    path('checkout', views.checkout, name='checkout'),
    path('checkout_shipping', views.checkout_shipping, name='checkout_shipping'),
    path('order_overview', views.order_overview, name='order_overview'),

    path('add_address', views.add_address, name='add_address'),
    path('delete_useraddress', views.delete_useraddress, name='delete_useraddress'),
]
