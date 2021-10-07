from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User, auth
from cart.views import _cart_id
from admin_panel.models import *
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

from cart.models import Cart, CartItem, UserAddress
from order.models import Order, OrderProduct


# import requests

# Create your views here.



def login(request):

    if request.session.has_key('user'):
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            print('credential entered')
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
                                print("inside try")
                                cart = Cart.objects.get(cart_id=_cart_id(request))
                                if CartItem.objects.filter(cart_id=cart).exists():
                                    try:
                                        cart_item = CartItem.objects.filter(cart=cart)      
                                    except:
                                        pass
                                    for item in cart_item:
                                        item.user = user
                                        item.save()
                            except:
                                pass
                            auth.login(request, user)
                            request.session['user'] = True
                            # url = request.META.get('HTTP_REFERER')
                            # try :
                            #     Query = requests.utils.urlparse(url).query
                            #     print('query ---',Query)
                            #     params = dict(x.split('=') for x in Query.split('&'))
                            #     if 'next' in params:
                            #         nextpage = params ['next']
                            #         return redirect(nextpage)
                            # except:
                            return redirect('index')
                                
                        else:
                            messages.info(request, 'invalid username or password')
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
                    print("created")
                    return redirect('login')
            else:
                messages.info(request, 'password not matching')
                return redirect('register')
    else:
        return render(request, 'account/register.html')



@login_required(login_url='login')
def logout(request):
    print('logged out')
    if request.session.has_key('user'):
        del request.session['user']
        auth.logout(request)
        print('logged out')
    return redirect('index')

@never_cache
def index(request):
    
    obj1 = Product.objects.all()
    context = {
        'product': obj1
    }
    return render(request, 'account/index.html', context)

def ProductPage(request, id):
    all_data = Product.objects.get(id=id)
    print(all_data)
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
    print(context)
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
    print("-----------------------------",user1.id)

    order_list = Order.objects.filter(user=request.user,is_ordered =True).order_by('created_at')
    order_count = order_list.count()
    if UserAddress.objects.filter(user_id=user1.id).exists():
        user_details = UserAddress.objects.filter(user_id=user1.id).last()
        print(user_details)
        context = {
            'user_details':user_details,
            'order_list' : order_list,
            'order_count':order_count,
        }
    else:
         context = {
            'order_list' : order_list,
            'order_count':order_count,
        }

    return render(request, 'account/user_profile.html',context) 


def order_cancel(request,order_number):

    get_order = Order.objects.filter(user=request.user.id,order_number=order_number)
    print(get_order)
    for order in get_order:
        order.status = 'Cancelled'
        order.save()
    messages.success(request,'order cancelled')
    return redirect('user_profile')

def edit_profile(request,id):
    print(id)
    datas = UserAddress.objects.get(id=id)
    if request.method == "POST":
        
        datas.first_name = request.POST['first_name']
        datas.last_name = request.POST['last_name']
        datas.email = request.POST['email']
        datas.phone_number = request.POST['phone_number']
        datas.save()
        messages.success(request,"profile updated successfully")
        return redirect('user_profile')
    else:
        context ={
            'data':datas
        }
    return render(request,'user_profile', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        print('inside post')
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user1 = User.objects.get(username__exact=request.user.username)
        print(user1)

        if new_password == confirm_password:
            success = user1.check_password(current_password)
            
            if success:
                print('inside success')
                user1.set_password(new_password)
                user1.save()
                print('saved')
                messages.success(request,"password updated successfully")
                return redirect('change_password')
            else:
                messages.error(request,'please enter valid password')
                return redirect('change_password')
        else:
            messages.error(request,"password doesn't match")
            return redirect('change_password')

    return redirect('user_profile')
