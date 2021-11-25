from .import views
from django.urls import path


urlpatterns = [

    path('',views.index,name='index'),
    path('register/',views.register,name='register'),
    path('login',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    
    path('otplogin/',views.otplogin,name='otplogin'),
    path('otpcheck/',views.otpcheck,name='otpcheck'),


    path('productpage/<id>',views.ProductPage,name='productpage'),

    path('search',views.search,name='search'),
    path('loginnavigation',views.loginnavigation,name='loginnavigation'),

    path('shop_clothes/',views.shop_clothes,name ='shop_clothes'),
    path('shop_footwears/',views.shop_footwears,name ='shop_footwears'),
    path('shopindianwears/',views.shopindianwears,name ='shopindianwears'),
    path('shopweasternwears/',views.shopweasternwears,name ='shopweasternwears'),

    path('user_profile',views.user_profile,name='user_profile'),
    path('change_password/',views.change_password,name='change_password'),
    
    path('order_cancel/<str:order_number>',views.order_cancel,name='order_cancel'),
    path('order_details/<str:order_number>',views.order_details,name='order_details'),
    path('editprofile',views.edit_profile,name='editprofile'),
]