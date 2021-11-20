from django.contrib.auth.models import User
from django.db import models
# from admin_panel.models import Product
from admin_panel.models import Product
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product

    


class UserAddress(models.Model):

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name          = models.CharField(max_length=100)
    last_name           = models.CharField(max_length=100)
    email               = models.EmailField(max_length=100)
    phone_number        = models.BigIntegerField(null=True)

    first_address            = models.CharField(max_length=100)
    second_address            = models.CharField(max_length=100)
    pin                 = models.CharField(max_length=6)

    city                = models.CharField(max_length=100)
    state               = models.CharField(max_length=100)
    country             = models.CharField(max_length=100)
    address_type        = models.CharField(max_length=100)

    def full_name(self):
        return f'{self.first_name}.{self.last_name}'

    def __str__(self):
        return self.first_name


class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
