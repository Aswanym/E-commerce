from django.contrib import admin
from django.urls import path
from .import views

urlpatterns=[
    
    path('order_complete/<str:order_number>',views.order_complete,name='order_complete'),
    path('payment/<str:order_number>',views.payment,name='payment'),
    path('paypal',views.paypal,name='paypal'),
    path('razorpay/<str:order_number>',views.razorpay,name='razorpay'),
    path('place_order/<int:count>',views.place_order,name='place_order'),

    path('order_status',views.order_status,name='order_status'),
    path('checkcoupon',views.checkcoupon,name='checkcoupon'),

    
]