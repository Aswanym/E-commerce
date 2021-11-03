from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import request
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User, auth
from admin_panel.models import Product,Offers
from order.models import Order, OrderProduct


from .models import Cart, CartItem, UserAddress
import datetime

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

'''   
private function that store the session key, if not session key create one.
'''

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # get the product
    cart = Cart.objects.filter(cart_id= _cart_id(request))
    current_user = request.user
    if current_user.is_authenticated: # if user already has an account
        try:
            # CartItem.objects.filter(product=product, user=current_user).exists() #check if product and user exist
            cart_item = CartItem.objects.get(product=product,user=current_user) 

            cart_item.quantity += 1
            cart_item.save()
        except :
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                # cart = cart,
                user = current_user,
            )
            cart_item.save()
    else:

        try:
            # get the cart using the cartid present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist: #if no cart create cart
            cart = Cart.objects.create( 
                cart_id=_cart_id(request)
            )
        cart.save()

        try: #if cart item already exist increment count
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()

        except CartItem.DoesNotExist: # if item is a new one create a new cart item
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            cart_item.save()
    return redirect('cart')


def minus_cart(request, product_id):

    if request.user.is_authenticated:
        
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, user=request.user)
        
    else:
        
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    shipping = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        
        else:
        
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            if cart_item.product.is_offer_avail == True:
                    total += (cart_item.product.offer_price * cart_item.quantity)
                    quantity += cart_item.quantity
            elif cart_item.product.category_offer_avail == True:
                total += (cart_item.product.category_offer_price * cart_item.quantity)
                quantity += cart_item.quantity
            else:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity

        tax  = int ( (2 * total)/100 )
        total_with_tax = total + tax

        if total_with_tax >= 1200:
            shipping = 0
        else:
            shipping = 80
        grand_total = total_with_tax + shipping

        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'shipping': shipping,
            'tax':tax,
            'grand_total': grand_total,
        }
    except ObjectDoesNotExist:
        total=0
        grand_total=0
        tax=0
        quantity=0
        shipping=0
        cart_items=0

        context = {
            'total': total,
            'grand_total':grand_total,
            'tax': tax,
            'shipping': shipping,
            'quantity': quantity,
            'cart_items': cart_items,
        
        }
    return render(request, 'account/cart.html', context)


def delete_cart(request, product_id):

    if request.user.is_authenticated:
        
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, user=request.user)
        cart_item.delete()
        return redirect('cart')

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
        return redirect('cart')

# def buy_now(request):
#     pass

def checkout_shipping(request):
    return redirect('checkout')

@login_required(login_url = 'login')
def checkout(request):
    address_count = UserAddress.objects.filter(user=request.user).count()

    if request.method == 'POST':
        if address_count < 3:  

            first_name      = request.POST.get('first_name')
            last_name       = request.POST.get('last_name')
            email           = request.POST.get('email')
            phone_number    = request.POST.get('phone_number')

            first_address        = request.POST.get('address1')
            second_address        = request.POST.get('address2')
            pin             = request.POST.get('pin')

            country         = request.POST.get('country')
            city            = request.POST.get('city')
            state           = request.POST.get('state')

            address_type    = request.POST.get('address_type')

        
            user_address = UserAddress.objects.create(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                phone_number=phone_number, 
                first_address=first_address,
                second_address=second_address, 
                pin=pin, 
                country=country, 
                city=city, 
                state=state, 
                address_type=address_type,
                user_id =request.user.id
                )
            user_address.save()
            
            messages.info(request,"select address and proceed.")
            return redirect('checkout')
            
        else:
            messages.error(request,"Cann't add more than 3 address")
            return redirect('checkout')

    else:
        
        useraddress = UserAddress.objects.filter(user_id = request.user )
        context = {
            'useraddress':useraddress,
            'address_count':address_count,
        }
        return render(request,'store/checkout.html',context)
    
def add_address(request):
    return render(request,'store/address_page.html')

def delete_useraddress(request):
    if request.method == "GET":
        useraddress_id=request.GET.get('addressid')
        delete_address = UserAddress.objects.get(id=useraddress_id)
        delete_address.delete()
        return JsonResponse({'msg':'delete success'})
    return JsonResponse({'msg':'message couldnot delete'})

def order_overview(request,total=0, quantity=0, cart_items=None):
    shipping = 0
    grand_total = 0
    razorpay_amount = 0
   
    useraddress = UserAddress.objects.filter(user=request.user)
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
    for cart_item in cart_items:
        if cart_item.product.is_offer_avail:
            total += (cart_item.product.offer_price * cart_item.quantity)
            quantity += cart_item.quantity

        elif cart_item.product.category_offer_avail:
            total += (cart_item.product.category_offer_price * cart_item.quantity)
            quantity += cart_item.quantity
            
        else:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    
    tax  = int ( (2 * total)/100 )
    total_with_tax = total + tax

    if total_with_tax >= 1200:
        shipping = 0
    else:
        shipping = 80
    grand_total = total_with_tax + shipping
    razorpay_amount=grand_total*100


    if Order.objects.filter(user=request.user,is_ordered=False):
        order1 = Order.objects.get(user=request.user,is_ordered=False)

    else:
        useraddress =UserAddress.objects.filter(user=request.user).last()
        order1 = Order()
        order1.user=request.user
        order1.first_name = useraddress.first_name
        order1.last_name = useraddress.last_name
        order1.email = useraddress.email
        order1.first_address = useraddress.first_address
        order1.second_address = useraddress.second_address
        order1.city = useraddress.city
        order1.country = useraddress.country
        order1.state = useraddress.state
        order1.pin = useraddress.pin
        order1.phone = useraddress.phone_number

        order1.order_total = grand_total
        order1.ip = request.META.get('REMOTE_ADDR')
        order1.save()

        #generate order number
        year            = int (datetime.date.today().strftime('%y'))
        date            = int (datetime.date.today().strftime('%d'))
        month           = int (datetime.date.today().strftime('%m'))
        d               = datetime.date(year,month,date)
        current_date    = d.strftime("%Y%m%d")
        order_number    = current_date+str(order1.id)
        order1.order_number = order_number
        order1.save()

    
        
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'shipping': shipping,
        'grand_total': grand_total,
        'tax': tax,
        'order1' : order1,
        'razorpay_amount':razorpay_amount,
        'useraddress' : useraddress,  
        
    }
    return render(request,'store/order_over_view.html',context)
