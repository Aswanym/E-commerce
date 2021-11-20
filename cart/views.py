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
from .models import Cart, CartItem, UserAddress, Wishlist
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

def add_cart_ajax(request):

    product_id=request.GET.get('product_id')
    if request.GET.get('product_quantity'):
        product_quantity_input = int( request.GET.get('product_quantity') )

    else: 
        product_quantity_input = 1

    total =0
    grand_total=0
    tax=0    
    product_quantity = 0
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    if product.stock <1 :
        return JsonResponse({'status':False,'message':"Product Out Of Stock"})

    #if user is authenticated
    if current_user.is_authenticated:
      
        if CartItem.objects.filter(product=product, user=current_user).exists():
            cart_item = CartItem.objects.get(product=product, user=current_user)
            cart_item.quantity += product_quantity_input #custom quantity updation
            cart_item.save()
            product_quantity = cart_item.quantity # setting quantity
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = product_quantity_input,   #custom quantity updation
                user = current_user,
            )
            product_quantity = 1   # setting quantity
            cart_item.save()
        sub_total = cart_item.sub_total()  
        #=========================cart count
        cart_count=0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart= cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                #calculate subtotal tax and grand total====================
                if  product.offer_status() : #check if offer price exists
                    total += (cart_item.product.offer_price * cart_item.quantity)
                else:
                    total += (cart_item.product.price * cart_item.quantity)

            tax = int ( (2 * total)/100  )
            grand_total = total + tax                
        except Cart.DoesNotExist:
            cart_count = 0  
        
        return JsonResponse({'status':True,'message':"Product Added to Cart Succesfully",'cart_count':cart_count,'sub_total':sub_total,'product_quantity':product_quantity,'total':total,'tax':tax,'grand_total':grand_total})
    

    #if user is not autheticated
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += product_quantity_input      #custom quantity updation
            cart_item.save()
            product_quantity = cart_item.quantity 

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = product_quantity_input,     #custom quantity updation
                cart = cart,
            )
            product_quantity = 1

            cart_item.save()
        sub_total = cart_item.sub_total()  
        #=========================cart count
        cart_count=0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart= cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                #calculate subtotal tax and grand total====================
                if  product.offer_status() : #check if offer price exists

                    total += (cart_item.product.offer_price * cart_item.quantity)
                else:
                    total += (cart_item.product.price * cart_item.quantity) 
            tax = int ( (2 * total)/100  )
            grand_total = total + tax                
        except Cart.DoesNotExist:
            cart_count = 0
        
        return JsonResponse({'status':True,'message':"Product Added to Cart  Succesfully",'cart_count':cart_count,'sub_total':sub_total,'product_quantity':product_quantity,'total':total,'tax':tax,'grand_total':grand_total})

def add_cart(request,product_id):


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


def minus_cart(request):

    if request.method == "GET":
        product_id = request.GET.get('cartitem_id')

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
            count = cart_item.quantity
            logger.error('count=========',count)
            return JsonResponse({'msg':'success','count':count})
        else:
            pass
            # cart_item.delete()
            # count = cart_item.quantity
            # logger.error('count=========',count)
            # return JsonResponse({'msg':'confirm','message': 'confirm???','count':count})
    else:
        return JsonResponse({'msg':'error'})
    
def cart(request, total=0, quantity=0, cart_items=None):
    shipping = 0
    grand_total = 0
    user=0
    zipped_data=0
    subtotals=[]
    user=request.user
    try:
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            
        else:
        
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            if item.product.is_offer_avail and item.product.category_offer_avail:
                p=item.product.compare()
                subtotals.append(p*item.quantity)
            elif item.product.is_offer_avail:
                subtotals.append(item.product.offer_price*item.quantity)
            elif item.product.category_offer_avail:
                subtotals.append(item.product.category_offer_price*item.quantity)
            else:
                subtotals.append(item.product.price*item.quantity)

        for cart_item in cart_items:
            
            if cart_item.product.is_offer_avail and cart_item.product.category_offer_avail:
                total += (cart_item.product.compare() * cart_item.quantity)
                quantity += cart_item.quantity
            elif cart_item.product.is_offer_avail == True:
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
        zipped_data = zip(subtotals,cart_items)
        context = {
            'total': total,
            'quantity': quantity,
            'user':user,
            'cart_items': cart_items,
            'shipping': shipping,
            'tax':tax,
            'grand_total': grand_total,
            'subtotals':subtotals,
            'zipped_data':zipped_data
        }
    except ObjectDoesNotExist:
        total=0
        zipped_data=0
        grand_total=0
        user=0
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
            'subtotals':subtotals,
        }
    return render(request, 'account/cart.html', context)

def delete_cart(request):

        product_id = request.GET.get('cart_id')
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(product=product, user=request.user)
            cart_item.delete()
            cart_count = CartItem.objects.filter(user=request.user).count()
            return JsonResponse({ 'message': 'sucessfully deleted','cart_count':cart_count})

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(product=product_id, cart=cart)
            cart_item.delete()
            return JsonResponse({ 'message': 'sucessfully deleted'})
  
def checkout_shipping(request):
    return redirect('checkout')

@login_required(login_url = 'login')
def checkout(request):
    address_count = UserAddress.objects.filter(user=request.user).count()

    if request.method == 'POST':
        if address_count < 3:  

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email  = request.POST.get('email')
            phone_number = request.POST.get('phone_number')

            first_address = request.POST.get('address1')
            second_address = request.POST.get('address2')
            pin = request.POST.get('pin')

            country = request.POST.get('country')
            city = request.POST.get('city')
            state = request.POST.get('state')

            address_type = request.POST.get('address_type')

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
    order_number=0
    subtotals=[]
   
    useraddress = UserAddress.objects.filter(user=request.user)
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    for item in cart_items:
        if item.product.is_offer_avail and item.product.category_offer_avail:
                p=item.product.compare()
                subtotals.append(p*item.quantity)
        elif item.product.is_offer_avail:
            subtotals.append(item.product.offer_price*item.quantity)
        elif item.product.category_offer_avail:
            subtotals.append(item.product.category_offer_price*item.quantity)
        else:
            subtotals.append(item.product.price*item.quantity)
       
        
    for cart_item in cart_items:

        if cart_item.product.is_offer_avail and cart_item.product.category_offer_avail:
            total += (cart_item.product.compare() * cart_item.quantity)
            quantity += cart_item.quantity

        elif cart_item.product.is_offer_avail:
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
    zipped_data = zip(subtotals,cart_items)

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

    order_number=order1.order_number   

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'shipping': shipping,
        'grand_total': grand_total,
        'tax': tax,
        'order1' : order1,
        'order_number':order_number,
        'razorpay_amount':razorpay_amount,
        'useraddress' : useraddress,   
        'zipped_data':zipped_data  
    }
    return render(request,'store/order_over_view.html',context)

@login_required(login_url = 'login')
def add_wishlist(request):

    if request.method == "GET":
        p_id=request.GET.get('product_id')
        data={}
        product = Product.objects.get(id=p_id)
        checkwishlist = Wishlist.objects.filter(product=product,user=request.user).count()
        wishlist_count = Wishlist.objects.all().count()
        if checkwishlist >0:
            data={
                'bool':False,
            }
        else:
            wishlist = Wishlist.objects.create(product=product,user=request.user)

            data={
                'bool':True,
                'wishlist_count':wishlist_count
            }
    return JsonResponse(data)

def show_wishlist(request):

    wishlists = Wishlist.objects.all()
    context={
        'wishlists': wishlists,  
    }
    return render(request,'account/wishlist.html',context)

def delete_wishlist(request):
    if request.method == "GET":
        product_id=request.GET.get('pro_id')
        delete_Wlist = Wishlist.objects.get(product=product_id)
        delete_Wlist.delete()
        return JsonResponse({'msg':'delete success'})
    return JsonResponse({'msg':'message couldnot delete'})

        
