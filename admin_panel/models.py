from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import BooleanField
from django.db.models.signals import ModelSignal, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify, truncatechars
from django.urls import reverse
from django.contrib.auth.models import User

import datetime



# Create your models here.
class Category(models.Model):

    category_name = models.CharField(max_length = 100,unique = True)
    category_description = models.TextField(max_length = 100,blank = True)
    slug = models.CharField(max_length = 100,unique = True)

    def __str__(self) :
        return self.category_name

class SubCategory(models.Model):

    sub_category                = models.CharField(max_length = 100,unique = True)
    sub_category_description    = models.TextField(max_length = 100,blank = True)
    sub_category_slug           = models.CharField(max_length = 100,unique = True)
    category                    = models.ForeignKey(Category,on_delete= models.CASCADE)

    def __str__(self) :
        return self.sub_category

class Product(models.Model):
    product_name         = models.CharField(max_length = 200)
    product_slug         = models.SlugField(max_length = 200, unique = True)
    product_description  = models.TextField(max_length = 500, blank = True)
    
    price        = models.IntegerField()
    stock        = models.PositiveIntegerField()

    image1       = models.ImageField(upload_to='medias',blank = False)
    image2       = models.ImageField(upload_to='medias',blank = False)
    image3       = models.ImageField(upload_to='medias',blank = False)
    image4       = models.ImageField(upload_to='medias',blank = False)

    is_offer_avail = models.BooleanField(default=False)
    offer_price = models.FloatField(null=True)
    expired = models.BooleanField(default=False,null=True)

    category    = models.ForeignKey(Category,on_delete= models.CASCADE)
    subcategory  = models.ForeignKey(SubCategory,on_delete= models.CASCADE)

    category_offer_avail = models.BooleanField(default=False)
    category_offer_price = models.FloatField(null=True)

    def get_url(self):
        return reverse('productpage',args=[self.id])

    def offer_status(self):
        date_time = datetime.date.today()
        today = date_time.strftime("%Y-%m-%d")
        if Offers.objects.filter(product=self).exists():
            all_offers = Offers.objects.get(product=self)
            if today <= str(all_offers.enddate) :
                
                all_offers.product.is_offer_avail=True
                all_offers.product.save()
                return True
            else:
                all_offers.product.is_offer_avail=False
                all_offers.product.expired = True
                all_offers.product.save()
                return False
            
    def offer_per(self):
        if Offers.objects.filter(product=self).exists():
            all_offers = Offers.objects.get(product=self)
            return all_offers.dis_percentage

    def savings(self):
        if Offers.objects.filter(product=self).exists():
           # all_offers = Offers.objects.get(product=self)
            save = self.price - self.offer_price
            print(save)
            return save

    def cat_offer_status(self):
        date_time = datetime.date.today()
        today = date_time.strftime("%Y-%m-%d")
        if CategoryOffers.objects.filter(category = self.category.id).exists():
            all_offers = CategoryOffers.objects.get(category = self.category.id)
            if today <= str(all_offers.enddate) :
                
                self.category_offer_avail = True
                self.save()
                return True
            else:
                self.category_offer_avail = False
                self.save()
                return False

    def cat_offer_per(self):
        if CategoryOffers.objects.filter(category = self.category.id).exists():
            all_offers = CategoryOffers.objects.get(category = self.category.id)
            return all_offers.dis_percentage

    def cat_savings(self):
        if CategoryOffers.objects.filter(category = self.category.id).exists():
           # all_offers = Offers.objects.get(product=self)
            save = self.price - self.category_offer_price
            print(save)
            return save

    def __str__(self) :
        return self.product_slug


    def compare(self):
        if CategoryOffers.objects.filter(category=self.category.id).exists() and Offers.objects.filter(product=self).exists():
            if self.offer_price <= self.category_offer_price:
                result = self.offer_price 
            else:
                result = self.category_offer_price 
            return result
        else:
            pass


@receiver(pre_save,sender = SubCategory)
def my_callback(sender, instance, *args, **kwargs):
    instance.sub_category_slug = slugify(instance.sub_category)

@receiver(pre_save,sender = Category)
def my_newcallback(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.category_name)

@receiver(pre_save,sender = Product)
def my_newmycallback(sender, instance, *args, **kwargs):
    instance.product_slug = slugify(instance.product_name)


class Offers(models.Model):
    offername = models.CharField(max_length = 200,blank=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,blank=False)
    dis_percentage = models.IntegerField(blank=False)
    is_avail = BooleanField(default=True,null=True)
    enddate = models .DateField(blank=False)

    def __str__(self):
        return self.offername


class CategoryOffers(models.Model):

    offername = models.CharField(max_length = 200,blank=False)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,blank=False)
    dis_percentage = models.IntegerField(blank=False)
    is_avail = BooleanField(default=True,null=True)
    enddate = models .DateField(blank=False) 

    def __str__(self):
        return self.offername

from order.models import OrderProduct      
class CouponOffer(models.Model):

    coupon_title=models.CharField(max_length=30,unique=True)  
    coupon_limit=models.IntegerField(blank = False)
    coupon_offer=models.FloatField(blank = False)
    coupon_end=models.DateField(blank = False)
    is_available = models.BooleanField(default= True)

    def coupon_expiry(self):
        date_time = datetime.date.today()
        today = date_time.strftime("%Y-%m-%d")
        
        print(str(self.coupon_end) < today,"===============check expired Coupon")
        if str(self.coupon_end) > today and  self.is_available == True :
            return False #not expired
        else:
            self.is_available = False
            self.save()
            return True  #expired
    
class CouponUsed(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    coupon = models.ForeignKey(CouponOffer,on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)
    order_number=models.CharField(max_length=100,null=True)
   


# Create your models here.

class BannerUpdate(models.Model):
    banner_image    = models.ImageField(blank = True,upload_to = 'banner_images')
    banner_name     = models.CharField(max_length=50)
    valid_from      = models.DateTimeField()
    valid_to        = models.DateTimeField()
    is_active       = models.BooleanField()
    created_at      = models.DateTimeField(auto_now_add=True)
 
    def _str_(self):
        return self.banner_name



