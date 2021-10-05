from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse

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
    stock        = models.IntegerField()

    image1       = models.ImageField(upload_to='medias',blank = False)
    image2       = models.ImageField(upload_to='medias',blank = False)
    image3       = models.ImageField(upload_to='medias',blank = False)
    image4       = models.ImageField(upload_to='medias',blank = False)

    subcategory  = models.ForeignKey(SubCategory,on_delete= models.CASCADE)

    def get_url(self):
        return reverse('productpage',args=[self.id])

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


