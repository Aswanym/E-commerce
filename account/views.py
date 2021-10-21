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


def login(request):

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
                    return redirect('login')
            else:
                messages.info(request, 'password not matching')
                return redirect('register')
    else:
        return render(request, 'account/register.html')


@login_required(login_url='login')
def logout(request):

    if request.session.has_key('user'):
        del request.session['user']
        auth.logout(request)
    return redirect('index')


@never_cache
def index(request):
    product = Product.objects.all()
    context = {
        'product': product,
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


@login_required(login_url='login')
def user_profile(request):
    user1 = User.objects.get(id=request.user.id)

    order_list = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')
    order_count = order_list.count()
    if UserAddress.objects.filter(user_id=user1.id).exists():
        user_details = UserAddress.objects.filter(user_id=user1.id).last()

        context = {
            'user_details': user_details,
            'order_list': order_list,
            'order_count': order_count,
        }
    else:
        context = {
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


def edit_profile(request, id):

    datas = UserAddress.objects.get(id=id)
    if request.method == "POST":
        datas.first_name = request.POST['first_name']
        datas.last_name = request.POST['last_name']
        datas.email = request.POST['email']
        datas.phone_number = request.POST['phone_number']
        datas.save()
        messages.success(request, "profile updated successfully")
        return redirect('user_profile')
    else:
        return redirect('user_profile')


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
