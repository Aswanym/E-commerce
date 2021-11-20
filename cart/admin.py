from cart.models import Cart, CartItem, Wishlist
from django.contrib import admin

# Register your models here.
admin.site.register( Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)