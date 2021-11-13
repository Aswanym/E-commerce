from django.contrib import admin
from .models import Category, SubCategory,Product,Offers,BannerUpdate,CouponUsed,CouponOffer,CategoryOffers

class ProductAdmin(admin.ModelAdmin):
             
    prepopulated_fields = {'product_slug':('product_name',)}
    
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product,ProductAdmin)
admin.site.register(Offers)
admin.site.register(BannerUpdate)
admin.site.register(CouponUsed)
admin.site.register(CouponOffer)
admin.site.register(CategoryOffers)

