from django.core.checks import messages
from django.contrib import messages
from django.http.response import JsonResponse
from cart.models import CartItem, UserAddress
from django.shortcuts import render,redirect
from order.models import Order, OrderProduct,Payment
from admin_panel.models import CouponOffer, Product, CouponUsed
from django.contrib.auth.models import User, auth
import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import razorpay

# Create your views here.

def checkcoupon(request):

    if request.method=="GET":
        couponname = request.GET.get('coupon')
        grand_total = request.GET.get('total_ammount')
        order_number = request.GET.get('order_number')

        if CouponOffer.objects.filter(coupon_title=couponname,is_available = True):
        
            coupon_instance = CouponOffer.objects.get(coupon_title=couponname,is_available = True)

            if coupon_instance.coupon_expiry() :
                return JsonResponse({'status':'expired','message':"Coupon Expired"})

            elif CouponUsed.objects.filter(user=request.user,coupon=coupon_instance,is_ordered = True).exists():
                return JsonResponse({'status':'used','message':"Coupon already used" })

            elif CouponUsed.objects.filter(user=request.user,coupon=coupon_instance ,is_ordered = False).exists():

                use_coupon=CouponUsed.objects.get(user=request.user,coupon=coupon_instance)
               
            else:
                use_coupon=CouponUsed()

            use_coupon.user = request.user
            use_coupon.coupon = coupon_instance
            use_coupon.order_number = order_number
            use_coupon.save()
            val = float(grand_total)

            percent_value = (float(grand_total)*coupon_instance.coupon_offer/100)

            if percent_value > coupon_instance.coupon_limit:
                grand_total = float(grand_total )- (coupon_instance.coupon_limit)
                coupon_price = coupon_instance.coupon_limit
            else:
                grand_total = int(float(grand_total) - percent_value)
                coupon_price= int(percent_value)

            
            order = Order.objects.get(user=request.user,order_number=order_number)
            order.coupon_price = grand_total
            order.save()

            return JsonResponse({'status':'success','message': ' coupon applied sucessfully','grand_total':grand_total,'coupon_price':coupon_price})
        return JsonResponse({'status':'error','message': 'coupon not available'})

@login_required(login_url = 'login')  
def place_order(request,count, total=0, quantity=0):

    shipping = 0
    grand_total = 0
    tax=0
    if count == 0 :
        messages.error(request,"Add address and proceed")
        return redirect('checkout')
    else:
        address_id = request.POST.get('address-id')

        cart_items = CartItem.objects.filter(user=request.user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('cart')


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

        if Order.objects.filter(user=request.user,is_ordered=False).exists():
            data = Order.objects.filter(user=request.user,is_ordered=False)

            for object in data:
                object.save()
            return redirect('order_overview')

        else:
            data = Order()
            if UserAddress.objects.filter(id=address_id).exists():
                useraddress = UserAddress.objects.get(id=address_id)    
                if request.method == 'POST':
                    
                    data.user=request.user
                    data.first_name = useraddress.first_name
                    data.last_name = useraddress.last_name
                    data.email = useraddress.email
                    data.first_address = useraddress.first_address
                    data.second_address = useraddress.second_address
                    data.city = useraddress.city
                    data.country = useraddress.country
                    data.state = useraddress.state
                    data.pin = useraddress.pin
                    data.phone = useraddress.phone_number
                    data.tax = tax 
                    data.order_total = grand_total
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.save()

                    #generate order number
                    year            = int (datetime.date.today().strftime('%y'))
                    date            = int (datetime.date.today().strftime('%d'))
                    month           = int (datetime.date.today().strftime('%m'))
                    d               = datetime.date(year,month,date)
                    current_date    = d.strftime("%Y%m%d")
                    order_number    = current_date+str(data.id)
                    data.order_number = order_number
                    data.save()
                    return redirect('order_overview')

                else:
                    return redirect('order_overview')
            else:
                return redirect('checkout')

def payment(request,order_number,total=0,quantity=0):
    tax=0
    couponuse=0
    orders = Order.objects.filter(user= request.user,is_ordered = False,order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    
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

    payment_method = request.POST.get('payment-option')

    if payment_method == 'cash':
        payment = Payment(user=request.user,payment_id=order_number,payment_method="COD",amount_paid=grand_total,status="completed")
        payment.save()
    
    for order in orders:
        order.payment = payment
        order.is_ordered = True
        order.save()

        # move the cartitems to the order product table

        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user = request.user
            orderproduct.product_id = item.product.id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.payment = payment
            orderproduct.status = "Ordered"
            orderproduct.save()

            #reduce the quantity of sold product

            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

            order_id = orderproduct.order_id 

            if CouponUsed.objects.filter(order_number=order_number,is_ordered=False).exists():
                couponuse = CouponUsed.objects.get(order_number=order_number)
                couponuse.is_ordered = True
                couponuse.save()
            # else:
            #     couponuse = CouponUsed.objects.get(order_number=order_number)
            #     couponuse.is_ordered = False
            #     couponuse.save()


        #clear cart
        CartItem.objects.filter(user=request.user).delete()

    return redirect('order_complete',order_number)

def paypal(request):
    body = json.loads(request.body)
    orders =Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

    # store transaction details inside payment model

    payment = Payment(
        user= request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = orders.order_total,
        status = body['status'],
    )
    payment.save()

    orders.status = "Ordered"
    orders.payment = payment
    orders.is_ordered = True
    orders.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = orders.id
        orderproduct.user = request.user
        orderproduct.product_id = item.product.id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.payment = payment
        orderproduct.status = "Ordered"

        orderproduct.save()

        #reduce the quantity of sold product
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()      

    #clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send order number and transaction id back to the sendData method via JsonResponse

    data={
        'order_number':orders.order_number,
        'transID' : payment.payment_id,     
    }
    return JsonResponse(data)

def razorpay(request,order_number,total=0,quantity=0):

    orders = Order.objects.filter(user= request.user,is_ordered = False, order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    
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
    payment_method = request.POST.get('payment-option')
    
    if request.method == 'POST':
        payment = Payment(user=request.user,payment_id=order_number,payment_method="razorpay",amount_paid=grand_total,status="Complete")
        payment.save()
    for order in orders:
        
        order.payment = payment
        order.status = "Ordered"
        order.is_ordered = True
        order.save()

        # move the cartitems to the order product table

        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user = request.user
            orderproduct.product_id = item.product.id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.payment = payment
            orderproduct.status = "Ordered"
        
            orderproduct.save()

            #reduce the quantity of sold product

            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

            
            if CouponUsed.objects.filter(order_number=order_number,is_ordered=False).exists():
                couponuse = CouponUsed.objects.get(order_number=order_number)
                couponuse.is_ordered = True
                couponuse.save()
            # else:
                
            #     couponuse = CouponUsed.objects.get(order_number=order_number)
            #     couponuse.is_ordered = False
            #     couponuse.save()

        #clear cart
        CartItem.objects.filter(user=request.user).delete()
    
    return redirect('order_complete',order_number)

def order_complete(request,order_number):
    offer_total = 0
    orginal_price = 0
    savings = 0
    total = 0
    coupon_use=0
    subtotals = []
    savings = []


    order_confirms = Order.objects.get(user=request.user,order_number=order_number)

    order_product = OrderProduct.objects.filter(user=request.user,order_id=order_confirms.id)

    for item in order_product:
        
        if item.product.is_offer_avail and item.product.category_offer_avail:
            p=item.product.compare()
            subtotals.append(p*item.quantity)
      
        elif item.product.is_offer_avail:
            subtotals.append(item.product.offer_price*item.quantity)
        elif item.product.category_offer_avail:
            subtotals.append(item.product.category_offer_price*item.quantity)
        else:
            subtotals.append(item.product.price*item.quantity)

    for order in order_product:

        if order.product.is_offer_avail and order.product.category_offer_avail:
            orginal_price = order.quantity * order.product.price
            offer_total = order.quantity * order.product.compare()
            savings = orginal_price - offer_total
            # total += (order.product.compare() * order.quantity)
            # quantity += order.quantity
        
        elif order.product.is_offer_avail == True:
            orginal_price = order.quantity * order.product.price
            offer_total = order.quantity * order.product.offer_price
            savings = orginal_price - offer_total

        elif order.product.category_offer_avail == True:
            orginal_price = order.quantity * order.product.price
            offer_total = order.quantity * order.product.category_offer_price
            savings = orginal_price - offer_total
        
        else:
            orginal_price = order.quantity * order.product.price

        zipped_data = zip(subtotals,order_product)

    if CouponUsed.objects.filter(order_number=order_number).exists():
        coupon_use =  CouponUsed.objects.get(order_number=order_number)
    


    context={
        'total':total,
        'order_confirms': order_confirms,
        'order_product': order_product,
        'offer_total':offer_total,
        'orginal_price':orginal_price,
        'savings':savings,
        'coupon_use':coupon_use,
        'zipped_data':zipped_data
    }
    return render(request,'store/order_complete.html',context)

@csrf_exempt
def order_status(request):
   
    if request.method == "POST":
        get_data = request.POST.get('optionVal')
        get_order =request.POST['ordernumber']
        orders = Order.objects.filter(order_number = get_order)
 
        order_products = OrderProduct.objects.filter(user_cancelled = False)

        for order in orders:
            order.status = get_data
            order.save()

        for orderproduct in order_products:
            orderproduct.status = get_data
            orderproduct.save()

        return JsonResponse({
                    'msg':'success',
                    'message':'Order status updated',
                })