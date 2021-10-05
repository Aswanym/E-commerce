from django.urls import path
from .import views


urlpatterns = [

    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>', views.add_cart, name='add_cart'),
    path('minus_cart/<int:product_id>', views.minus_cart, name='minus_cart'),
    path('delete_cart/<product_id>', views.delete_cart, name='delete_cart'),

    path('checkout', views.checkout, name='checkout'),
    path('add_address', views.add_address, name='add_address'),
    path('checkout_shipping', views.checkout_shipping, name='checkout_shipping'),
    path('order_overview', views.order_overview, name='order_overview'),

]
