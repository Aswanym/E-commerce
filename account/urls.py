from .import views
from django.urls import path


urlpatterns = [
    path('',views.index,name='index'),
    path('register/',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout/',views.logout,name='logout'),

    path('productpage/<id>',views.ProductPage,name='productpage'),

    path('shop_clothes/',views.shop_clothes,name ='shop_clothes'),
    path('shop_footwears/',views.shop_footwears,name ='shop_footwears'),

    path('user_profile/',views.user_profile,name='user_profile'),
    path('change_password/',views.change_password,name='change_password'),
    path('edit_profile/<int:id>',views.edit_profile,name='edit_profile'),
    path('order_cancel/<str:order_number>',views.order_cancel,name='order_cancel'),

]