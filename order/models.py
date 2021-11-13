from cart.models import UserAddress
from django.db import models
from django.contrib.auth.models import User
from admin_panel.models import Product
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.FloatField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Order(models.Model):

    STATUS =(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Shipped','Shipped'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled')
    ) 

    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number=models.CharField(max_length=100,null=True)

    first_name=models.CharField(max_length=50,null=False)
    last_name=models.CharField(max_length=50,null=False)
    phone=models.CharField(max_length=10,null=False)
    email=models.EmailField(max_length=50,null=False)

    first_address=models.CharField(max_length=50,null=False)
    second_address=models.CharField(max_length=50,blank=True)
    pin = models.CharField(max_length=6)
    
    city=models.CharField(max_length=50,null=False)
    state=models.CharField(max_length=50,null=False)  
    country=models.CharField(max_length=50,null=False)  
    
    order_total=models.FloatField(null=True)
    
    status=models.CharField(max_length=30,choices=STATUS,default='New')
    ip=models.CharField(max_length=100,blank=True)
    tax=models.FloatField(null=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    coupon_price=models.FloatField(null=True,blank=True)
        
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.first_address} {self.second_address}'

    # def __str__(self):
    #     return self.first_name

class OrderProduct(models.Model):

    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    status=models.CharField(default='Pending',max_length=20,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user_cancelled=models.CharField(default=False,max_length=20,null=True)
    
    

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.product.product_name
            
