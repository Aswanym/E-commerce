from django.db import models
from django.db.models.fields import BooleanField
from django.db.models.signals import ModelSignal, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify, truncatechars
from django.urls import reverse

import datetime




# Create your models here.
class Category(models.Model):

    category_name           = models.CharField(max_length = 100,unique = True)
    category_description    = models.TextField(max_length = 100,blank = True)
    slug                    = models.CharField(max_length = 100,unique = True)

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

    is_offer_avail = models.BooleanField(default=False,null=True)
    offer_price = models.FloatField(null=True)
    expired = models.BooleanField(default=False,null=True)

    subcategory  = models.ForeignKey(SubCategory,on_delete= models.CASCADE)

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
                all_offers.product.save()
                return False

    def __str__(self) :
        return self.product_slug

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

       

