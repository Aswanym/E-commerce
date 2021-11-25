from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User, auth

from cart.views import _cart_id
from admin_panel.models import *
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem, UserAddress
from order.models import Order, OrderProduct
from account.models import UserProfile
from django.db.models import Q
from django.core.paginator import Paginator

from django.views.decorators.cache import cache_control
from twilio.rest import Client
from private import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SERVICE_SID

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def login(request):

    if request.session.has_key('user') and request.user.is_active:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            if username == '' or password == '':
                messages.info(request, 'Enter all fields')
                return redirect('login')
            else:
                if User.objects.filter(username=username).exists():
                    us = User.objects.get(username=username)
                    if us.is_active:
                        user = auth.authenticate(
                            username=username,
                            password=password)
                        if user is not None:
                            try:
                                cart = Cart.objects.get(
                                    cart_id=_cart_id(request))
                                if CartItem.objects.filter(cart_id=cart).exists():
                                    try:
                                        cart_item = CartItem.objects.filter(
                                            cart=cart)
                                    except:
                                        pass
                                    for item in cart_item:
                                        item.user = user
                                        item.save()
                            except:
                                pass
                            auth.login(request, user)
                            request.session['user'] = True
                            return redirect('index')
                        else:
                            messages.info(
                                request, 'invalid username or password')
                            return redirect('login')
                    else:
                        messages.info(request, 'You are blocked')
                        return redirect('login')
                else:
                    messages.info(request, 'invalid username or password')
                    return redirect('login')
        else:
            return render(request, 'account/login.html')


def register(request):

    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_no = request.POST.get('phone_no')
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        

        if username == '' or password1 == '' or first_name == '' or email == '' or last_name == '':
            messages.info(request, 'Varify all fields')
            return redirect('register')


        else:
            if password1 == password2:
                if User.objects.filter(username=username).exists():
                    messages.info(request, 'username already exist')
                    return redirect('register')
                elif User.objects.filter(email=email).exists():
                    messages.info(request, 'Email already exist')
                    return redirect('register')
                else:
                    user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                                    email=email, password=password1, username=username)
                    user.save()
                    user_profile =  UserProfile(phone_no=phone_no)
                    user_profile.save()

                    return redirect('login')
            else:
                messages.info(request, 'password not matching')
                return redirect('register')
    else:
        return render(request, 'account/register.html')

def otplogin(request):
    if request.method == "POST":
        phone_no = request.POST.get('phone_no')

        if UserProfile.objects.filter(phone_number=phone_no).exists():
            mobile = UserProfile.objects.filter(phone_number=phone_no)
            for i in mobile:
                mobile_no = i.phone_number
                user = i.user.username

            user_mobile = '+91'+ str(mobile_no)
            request.session['user_mobile'] = user_mobile
            request.session['username'] = user
            print('yyyyyyyyyyyyyyy',request.session['username'])

            auth_sid = TWILIO_ACCOUNT_SID
            auth_token = TWILIO_AUTH_TOKEN
            
            client = Client(auth_sid,auth_token)
            
            verification = client.verify \
                        .services(TWILIO_SERVICE_SID) \
                        .verifications \
                        .create(to= user_mobile, channel='sms')
            print('user exists')
            return redirect('otpcheck')

        else:
            print('not a registered user')
            messages.error(request,'not a registered user')
            return redirect('otplogin')
    return render(request,'account/otplogin.html')

def otpcheck(request):
    if request.method == "POST":
        otp_input = request.POST.get('otp')

        user_mobile = request.session['user_mobile']
        user = request.session['username'] 

        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        verification_check = client.verify \
                                .services(TWILIO_SERVICE_SID) \
                                .verification_checks \
                                .create(to= user_mobile, code= otp_input)

        print(verification_check.status)
        if verification_check.status == "approved":
            # messages.success(request,"OTP verified successfully.")
            user = User.objects.get(username=user)
            user.is_active = True           
            user.save()          
            auth.login(request,user)          
            try:
                print('inside try')
                del request.session['user_mobile']
                del request.session['username']
               
            except:
                print('inside except')
                
            return redirect('index') 
        else:
            messages.error(request,'wrong otp')
            return redirect('otplogin')             
    
    return render(request,'account/otpcheck.html')


@login_required(login_url='login')
def logout(request):

    if request.session.has_key('user'):
        del request.session['user']
        auth.logout(request)
        return redirect('index')
    else:
        # del request.session['user_mobile']
        # del request.session['username'] 
        auth.logout(request)
        return redirect('login')


@never_cache
def index(request):

    product = Product.objects.all()
    paginator = Paginator(product,8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'product': page_obj,
        
    }
    return render(request, 'account/index.html', context)


def ProductPage(request, id):
    all_data = Product.objects.get(id=id)
    in_cart = CartItem.objects.filter(
        cart__cart_id=_cart_id(request), product=all_data).exists()
    context = {
        'all_data': all_data,
        'in_cart': in_cart,
    }
    return render(request, 'account/product-page.html', context)


def shop_clothes(request):
    product = Product.objects.all()
    context = {
        'product': product
    }

    return render(request, 'account/shop_clothes.html', context)


def shop_footwears(request):
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'account/shop_footwears.html', context)


def shopindianwears(request):
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'account/shop_indianwears.html', context)


def shopweasternwears(request):
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'account/shop_weasternwears.html', context)


@login_required(login_url='login')
def user_profile(request):

    user_details = 0
    user_picture = 0
    order_list = 0
    order_count = 0

    get_user =User.objects.get(id= request.user.id)
    print(get_user)

    if UserProfile.objects.filter(user= get_user).exists():
        user_picture = UserProfile.objects.get(user=get_user)
    else:
        user_picture = UserProfile()
        user_picture.user = get_user
        user_picture.save()

    order_list = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')
    order_count = order_list.count()
    
    user_details = User.objects.filter(username=get_user)
    context = {
        'user_details': user_details,
        'user_picture': user_picture,
        'order_list': order_list,
        'order_count': order_count,
    }

    return render(request, 'account/user_profile.html', context)

def order_cancel(request, order_number):

    get_order = Order.objects.filter(
        user=request.user.id, order_number=order_number)
    for order in get_order:
        order_id = order.id
    order_products = OrderProduct.objects.filter(order_id=order_id)
    for order in get_order:
        order.status = 'Cancelled'
        order.save()
    for order_cancel in order_products:
        order_cancel.user_cancelled = True
        order_cancel.status = "Cancelled"
        order_cancel.save()

    messages.success(request, 'order cancelled')
    return redirect('user_profile')


def edit_profile(request):
    get_user = request.user.id
    print(get_user)

    logger.error('Something went wrong!', get_user)
    
    user = User.objects.get(id=get_user)

    if UserProfile.objects.filter(user=get_user).exists():

        profile = UserProfile.objects.get(user=get_user)
    else:
        profile = UserProfile()

    if request.method == "POST":
     
        profile.user.first_name = request.POST['first_name']
        profile.user.last_name = request.POST['last_name']
        profile.user.email = request.POST['email']
        profile.phone_number = request.POST['phone_number']
        profile.user.save()

        profile.profile_picture = request.FILES['pic']
        profile.user = user
        profile.save()
        messages.success(request, "profile updated successfully")
        return redirect('user_profile')
    else:

        return redirect(request, 'account/edit-profile.html')


@login_required(login_url='login')
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user1 = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user1.check_password(current_password)

            if success:
                user1.set_password(new_password)
                user1.save()

                return JsonResponse({
                    'msg': 'success',
                    'message': 'password updated successfully'
                })
            else:

                return JsonResponse({
                    'msg': 'invalid',
                    'message': 'please enter valid password'
                })
        else:

            return JsonResponse({
                'msg': 'notmatch',
                'message': "password doesn't match"
            })

    return redirect('user_profile')


def order_details(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order_detail = OrderProduct.objects.filter(order_id=order.id).last()
    order_details = OrderProduct.objects.filter(order_id=order.id)

    context = {
        'order': order,
        'order_detail': order_detail,
        'order_details': order_details,
    }
    return render(request, 'account/order_details.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):

    value = request.POST['search']
    if value == "":
        return redirect('index')
    else:
        data = Product.objects.filter(
            Q(product_name__icontains=value)).order_by("id")
        prod = Product.objects.all()
        prd_count = prod.count()
        count = data.count()
        context = {
            'products': data,
            "count": count,
            "prd_count": prd_count
        }
        return render(request, 'store/search-product.html', context)


def loginnavigation(request):
    if request.session.has_key('user'):
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            if username == '' or password == '':
                messages.info(request, 'Enter all fields')
                return redirect('login')
            else:
                if User.objects.filter(username=username).exists():
                    us = User.objects.get(username=username)
                    if us.is_active:
                        user = auth.authenticate(
                            username=username,
                            password=password)
                        if user is not None:
                            try:
                                cart = Cart.objects.get(
                                    cart_id=_cart_id(request))
                                if CartItem.objects.filter(cart_id=cart).exists():
                                    try:
                                        cart_item = CartItem.objects.filter(
                                            cart=cart)
                                    except:
                                        pass
                                    for item in cart_item:
                                        item.user = user
                                        item.save()
                            except:
                                pass
                            auth.login(request, user)
                            request.session['user'] = True
                            return redirect('cart')
                        else:
                            messages.info(
                                request, 'invalid username or password')
                            return redirect('login')
                    else:
                        messages.info(request, 'You are blocked')
                        return redirect('login')
                else:
                    messages.info(request, 'invalid username or password')
                    return redirect('login')
        else:
            return render(request, 'account/login.html')
