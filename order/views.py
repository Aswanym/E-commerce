from django.http.response import JsonResponse
from cart.models import CartItem, UserAddress
from django.shortcuts import render,redirect
from order.models import Order, OrderProduct,Payment
from admin_panel.models import Product
from django.contrib.auth.models import User, auth
import datetime
import json

import razorpay

# Create your views here.

def place_order(request, total=0, quantity=0):
    print("entered palce order")
    shipping = 0
    grand_total = 0

    address_id = request.POST.get('address-id')
    print("this is for test..........................",id)

    cart_items = CartItem.objects.filter(user=request.user)
    cart_count = cart_items.count()
    if cart_count <=0 :
        return redirect('account/cart')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    if total >= 1200:
        shipping = 0
    else:
        shipping = 80
    grand_total = total + shipping

    if Order.objects.filter(user=request.user,is_ordered=False).exists():
        data = Order.objects.filter(user=request.user,is_ordered=False)
    
        print(data)
        for object in data:
            object.save()
        return redirect('order_overview')

    else:
        data = Order()
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

def payment(request,order_number,total=0,quantity=0):
    
    orders = Order.objects.filter(user= request.user,is_ordered = False,order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    if total >= 1200:
        shipping = 0
    else:
        shipping = 80
    grand_total = total + shipping

    payment_method = request.POST.get('payment-option')

    if payment_method == 'cash':
        payment = Payment(user=request.user,payment_id=order_number,payment_method="COD",amount_paid=grand_total,status="completed")
        payment.save()
    print('payment successfull')
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
            orderproduct.save()

            #reduce the quantity of sold product

            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

            order_id = orderproduct.order_id 
            print("----------------------------",order_id)

        #clear cart
        CartItem.objects.filter(user=request.user).delete()

    return redirect('order_complete',order_number)

def paypal(request):
    body = json.loads(request.body)
    print(body)
    orders =Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

    # store transaction details inside payment model

    payment = Payment(
        user= request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = orders.order_total,
        status = body['status'],
    )
    print(payment)
    payment.save()

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
    print('hai')

    orders = Order.objects.filter(user= request.user,is_ordered = False, order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    if total >= 1200:
        shipping = 0
    else:
        shipping = 80
    grand_total = total + shipping
    print('inside payment option')
    payment_method = request.POST.get('payment-option')
    print('outside payment option',payment_method)
    if request.method == 'POST':
        payment = Payment(user=request.user,payment_id=order_number,payment_method="razorpay",amount_paid=grand_total,status="Complete")
        payment.save()
        print('payment successfull')
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
            orderproduct.status = "ordered"
            orderproduct.ordered = True
            orderproduct.payment = payment
            orderproduct.save()

            #reduce the quantity of sold product

            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

            order_id = orderproduct.order_id 
            print("-------------------------------------",order_id)
            print(type(order_id))
        #clear cart
        CartItem.objects.filter(user=request.user).delete()
    
    return redirect('order_complete',order_number)

def order_complete(request,order_number):
    
    print('inside order confirm')
    order_confirms = Order.objects.get(user=request.user,order_number=order_number)
    print(order_confirms)
    order_product = OrderProduct.objects.filter(user=request.user,order_id=order_confirms.id)
    # for product in order_product:
    #     print(product)
    
    context={
        'order_confirms': order_confirms,
        'order_product': order_product,
    }
    return render(request,'store/order_complete.html',context)