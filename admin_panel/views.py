from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.expressions import Window
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.db.models.functions import ExtractMonth
from admin_panel.models import Category, Offers, Product, SubCategory, CategoryOffers,CouponOffer
from order.models import Order, OrderProduct, Payment
import calendar
from django.db.models import Q

from django.db.models import Count,Sum,F
import os

from django.core.files.base import ContentFile
import base64
from admin_panel.forms import BannerUpdateForm
from admin_panel.models import BannerUpdate
from django.core.paginator import Paginator
import datetime


def adminlogin(request):
    if request.session.has_key('admin_login'):
        return redirect('admindash')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    auth.login(request, user)
                    request.session['admin_login'] = True
                    return redirect('admindash')
                messages.info(request, 'Not a user')
                return redirect('adminlogin')
            else:
                messages.info(request, 'Username or password incorrect')
                return redirect('adminlogin')
        else:
            return render(request, 'admin/adminlogin.html')


@login_required(login_url='adminlogin')
def admindash(request):
    if request.session.has_key('admin_login'):
        
        completed_order= OrderProduct.objects.filter(status = "Delivered")
        sales = OrderProduct.objects.aggregate(sales=Sum( F('product_price')*F('quantity') ))['sales']
        products = Product.objects.all()
        stock_avail = Product.objects.aggregate(stock=Sum(F('stock') ))['stock']

        revenue=0
        for one_order in completed_order:
            revenue += one_order.product_price*one_order.quantity
       
     #--------------------------------------payment graph----------------------------------------#
        payment_method = []
        payment_count = []
        pay_count = Payment.objects.filter(payment_method__in=('paypal', 'COD', 'razorpay')).values(
            'payment_method').annotate(count=Count('payment_method')).values('payment_method', 'count')

        for pay in pay_count:
            payment_method.append(pay['payment_method'])
            payment_count.append(pay['count'])

    #--------------------------------------product availability---------------------------------------#
        allproduct = []
        stock = []
        products = Product.objects.all().values('product_name').annotate(
            stock=Sum('stock')).values('product_name', 'stock')

        for product in products:
            allproduct.append(product['product_name'])
            stock.append(product['stock'])

    #--------------------------------user details------------------------------------------------#
        users = []
        user_count = []

        userall = User.objects.filter(is_active__in=('True', 'False')).values(
            'is_active').annotate(counter=Count('is_active')).values('is_active', 'counter')

        for user in userall:
            users.append(user['is_active'])
            user_count.append(user['counter'])
   
    #===========================================================================================================#
        last_six_order = Order.objects.filter(
            is_ordered=True).order_by('-id')[:6]

        admin_user = User.objects.get(id= request.user.id)

        context = {'last_six_order': last_six_order,
                   
                   'payment_method': payment_method,
                   'payment_count': payment_count,
                   'stock': stock,
                   'allproduct': allproduct,
                   'users': users,
                   'user_count': user_count,
                   'admin_user':admin_user,
                    "revenue":revenue,
                    "sales":sales,
                    "stock_avail":stock_avail,
                   }

        return render(request, 'admin/admindash.html', context)
    else:
        return redirect('adminlogin')


@login_required(login_url='adminlogin')
def adminlogout(request):
    auth.logout(request)
    return redirect('adminlogin')


def adminbase(request):
    return render(request, 'admin/adminbase.html')

#========================================  Product ==============================================#


@login_required(login_url='adminlogin')
def addproduct(request):

    image1 = 0
    image2 = 0
    image3 = 0
    image4 = 0
    if request.method == 'POST':

        data = Product()

        data.product_name = request.POST.get('product_name')
        data.category = Category.objects.get(
            category_name=request.POST.get('category'))
        data.subcategory = SubCategory.objects.get(
            sub_category=request.POST.get('subcategory'))
        data.product_description = request.POST.get('product_description')
        data.product_slug = request.POST.get('product_slug')

        data.price = request.POST.get('price')
        data.stock = request.POST.get('stock')

        

        if request.POST.get('pro_img1'):
            image1 = request.POST['pro_img1']
            format, img1 = image1.split(';base64,')
            ext = format.split('/')[-1]
            img_data1 = ContentFile(base64.b64decode(img1), name=request.POST.get('product_name') + '1.' + ext)

        if request.POST.get('pro_img2'):
            image2 = request.POST['pro_img2']
            format, img2 = image2.split(';base64,')
            ext = format.split('/')[-1]
            img_data2 = ContentFile(base64.b64decode(img2), name=request.POST.get('product_name') + '2.' + ext)
                # else:
                #     image2 = request.FILES['image2']

        if request.POST.get('pro_img3'):
            image3 = request.POST['pro_img3']
            format, img3 = image3.split(';base64,')
            ext = format.split('/')[-1]
            img_data3 = ContentFile(base64.b64decode(img3), name=request.POST.get('product_name') + '3.' + ext)
        # else:
        #     image3 = request.FILES['image3']

        if request.POST.get('pro_img4'):
            image4 = request.POST['pro_img4']
            format, img4 = image4.split(';base64,')
            ext = format.split('/')[-1]
            img_data4 = ContentFile(base64.b64decode(img4), name=request.POST.get('product_name') + '4.' + ext)

        data.image1 = img_data1
        data.image2 = img_data2
        data.image3 = img_data3
        data.image4 = img_data4


        data.save()
        return redirect('productlist')
    else:
        category = Category.objects.all()
        subcategory = SubCategory.objects.all()

        context = {'category': category,
                   'subcategory': subcategory
                   }
        return render(request, 'admin/add-product.html', context)

@login_required(login_url='adminlogin')
def edit_product(request,id):

    product_data = Product.objects.get(id=id)
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()

    if request.method == "POST":

        # if len(request.FILES !=0):
        #     if len(product_data.image1 > 0):
        #         os.remove(product_data.image1.path)
        #     product_data.image1 = request.FILES['pro_img1']
        
        product_data.product_name = request.POST.get('product_name')
        product_data.product_description = request.POST.get('product_description')
        product_data.price = request.POST.get('price')
        product_data.stock = request.POST.get('stock')
        product_data.category = Category.objects.get(
            category_name=request.POST.get('category'))
        product_data.subcategory = SubCategory.objects.get(
            sub_category=request.POST.get('subcategory'))

        product_data.image1 = request.FILES['pic1']
        product_data.image2 = request.FILES['pic2']
        product_data.image3 = request.FILES['pic3']
        product_data.image4 = request.FILES['pic4']
        

        product_data.save()
        messages.success(request,'Edited successfully')
        return redirect('productlist')
 
    context = {
        'category': category,
        'subcategory': subcategory,
        'product_data': product_data
    }    
    messages.success(request,'Edited successfully')
    return render(request,'admin/edit-product.html',context)

# @login_required(login_url='adminlogin')
# def EditProduct(request, id):
    
#     product_data = Product.objects.get(id=id)
#     category = Category.objects.all()
#     subcategory = SubCategory.objects.all()
#     context = {
#         'category': category,
#         'subcategory': subcategory,
#         'product_data': product_data
#     }
#     return render(request, 'admin/edit-product.html', context)


# @login_required(login_url='adminlogin')
# def EditedProduct(request, id):

#     data = Product.objects.get(id=id)
#     data.product_name = request.POST.get('product_name')
#     data.category = Category.objects.filter(
#         category_name=request.POST.get('category'))
#     data.product_description = request.POST.get('product_description')
#     data.product_slug = request.POST.get('product_slug')

#     data.price = request.POST.get('price')
#     data.stock = request.POST.get('stock')

#     if len(request.FILES) != 0:
#         if len(data.image1) > 0:
#             os.remove(data.image1.path)
#         data.image1 = request.FILES['pic1']
#         data.image2 = request.FILES['pic2']
#         data.image3 = request.FILES['pic3']
#         data.image4 = request.FILES['pic4']

#     data.save()
#     messages.success(request,'Edited successfully')
#     return redirect('productlist')
    


@login_required(login_url='/adminlogin/')
def productlist(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    data = Product.objects.filter(Q(product_name__icontains=search_query) | 
                                    Q(price__icontains=search_query))
    context = {'data': data,
                'search_query':search_query 
    }
    return render(request, 'admin/product-list.html', context)

def DeleteProduct(request):

    if request.method == "GET":
        id = request.GET.get('prod_offerid')
        data = Product.objects.get(id=id)
        data.delete()
        return JsonResponse({'msg': 'success', 'message': 'sucessfully deleted'})
    return JsonResponse({'message': 'wrong route'})


#========================================  Category ==============================================#


@login_required(login_url='adminlogin')
def addcategory(request):
    if request.method == 'POST':

        category_list = Category()
        category_list.category_name = request.POST.get('category_name')
        category_list.slug = request.POST.get('slug')
        category_list.category_description = request.POST.get(
            'category_description')
        category_list.save()
        # messages.success(request,'product added sucessfully')
        return redirect('categorylist')

    else:
        return render(request, 'admin/add-category.html')


@login_required(login_url='adminlogin')
def categorylist(request):

    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    all_category = Category.objects.filter(category_name__icontains=search_query)
    context = {'all_category': all_category,'search_query':search_query }
    return render(request, 'admin/category-list.html', context)

def editCategory(request,id):
    category_edit = Category.objects.get(id=id)
    if request.method == 'POST':
        category_edit.category_name = request.POST.get('category_name')
        category_edit.category_description = request.POST.get('category_description')
        category_edit.save()
        messages.success(request,'Edited successfully')
        return redirect('categorylist')
    
    return render(request,'admin/edit-category.html',{'category_edit':category_edit})


def deleteCatergory(request):

    if request.method == "GET":
        id = request.GET.get('cat_offerid')
        data = Category.objects.get(id=id)
        data.delete()
        return JsonResponse({'msg': 'success', 'message': 'sucessfully deleted'})
    return JsonResponse({'message': 'wrong route'})
    
#======================================== Sub Category ==============================================#


def AddSubCategory(request):

    if request.method == 'POST':
        sub_category_list = SubCategory()
        sub_category_list.sub_category = request.POST.get('sub_category')
        sub_category_list.sub_category_slug = request.POST.get(
            'sub_category_slug')
        sub_category_list.sub_category_description = request.POST.get(
            'sub_category_description')
        sub_category_list.category = Category.objects.get(
            category_name=request.POST.get('category'))
        sub_category_list.save()

        return redirect('subcategorylist')
    else:
        category = Category.objects.all()

        context = {'category': category}
        return render(request, 'admin/add-sub-category.html', context)


def SubCategoryList(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    category = Category.objects.all()
    all_sub_category = SubCategory.objects.filter(sub_category__icontains=search_query)
    context = {'all_sub_category': all_sub_category,
               'category': category,
               'search_query':search_query
               }
    return render(request, 'admin/sub-category-list.html', context)

def editSubCatergory(request,id):
    subcategory_edit = SubCategory.objects.get(id=id)
    category = Category.objects.all()
    if request.method == 'POST':
        subcategory_edit.sub_category  = request.POST.get('sub_category')
        subcategory_edit.category = Category.objects.get(category_name = request.POST.get('category')) 
        subcategory_edit.sub_category_description = request.POST.get('subcategorydescription')
        subcategory_edit.save()
        messages.success(request,'Edited successfully')
        return redirect('subcategorylist')
    
    return render(request,'admin/edit-subcategory.html',{'subcategory_edit':subcategory_edit,'category':category})


def deleteSubCatergory(request):

    if request.method == "GET":
        id = request.GET.get('subcat_offerid')
        data = SubCategory.objects.get(id=id)
        data.delete()
        return JsonResponse({'msg': 'success', 'message': 'sucessfully deleted'})
    return JsonResponse({'message': 'wrong route'})


#========================================  user ==============================================#


@login_required(login_url='adminlogin')
def userlist(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
    data = User.objects.filter(username__icontains=search_query)
    return render(request, 'admin/userlist.html', {'data': data,'search_query':search_query})

def userblock(request, id):

    data = User.objects.get(id=id)
    if data.is_active == True:
        data.is_active = False
        data.save()
        return redirect('userlist')
    else:
        data.is_active = True
        data.save()
        return redirect('userlist')

# ============================================order===================================


def orders(request):
    
    order_list = OrderProduct.objects.all()
    paginator = Paginator(order_list,10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/orders.html', {'order_list': page_obj})

# =======================================sales report====================================

def salesreport(request):

    if request.method == "POST":
        fdate = request.POST['fdate']
        ldate = request.POST['enddate']
        amount = 0
        try:
            check = True
            searchresult = OrderProduct.objects.filter(
                created_at__lte=ldate, created_at__gte=fdate)
            for result in searchresult:
                amount += result.payment.amount_paid
            return render(request, 'admin/sales-report.html', {'datas': searchresult, 'sum': amount, 'check': check})
        except:
            return redirect('salesreport')
    else:
        amount = 0
        check = False
        orderedproducts = OrderProduct.objects.all()
        data = OrderProduct.objects.filter(status='Delivered')
        for order in data:
            amount += order.payment.amount_paid
        return render(request, 'admin/sales-report.html', {'datas': orderedproducts, 'sum': amount, 'check': check})


# ==========================================productoffer===========================================================
def productoffer(request):

    products = Product.objects.all()

    if request.method == "POST":
        if Product.objects.filter(product_name=request.POST.get('product_name'), is_offer_avail=True).exists():
            messages.success(request, 'Offer for this product already exists')
            return redirect('productoffer')
        else:
            product_offer = Offers()
            product_offer.offername = request.POST.get('offername')
            product_offer.product = Product.objects.get(
                product_name=request.POST.get('product_name'))
            product_offer.dis_percentage = request.POST.get('offer')
            product_offer.enddate = request.POST.get('enddate')
            product_offer.save()

            offer_avail_product = Product.objects.get(
                product_name=request.POST.get('product_name'))
            offer = Offers.objects.get(product=offer_avail_product.id)

            # calculate the discount price
            offer_percent = int(offer.dis_percentage)
            product_price = offer_avail_product.price
            savings = (product_price * offer_percent)/100
            dicounted_price = product_price-savings

            # save discount details in product table
            offer_avail_product.offer_price = dicounted_price
            offer_avail_product.is_offer_avail = True
            offer_avail_product.save()

            messages.success(request, 'Offer added successfully')
            return redirect('productoffer')
    else:
        return render(request, 'admin/productoffer.html', {'products': products})


def productofferlist(request):
    offer_list = Offers.objects.all()
    return render(request, 'admin/productoffer-list.html', {'offer_list': offer_list})


def delete_product_offer(request):

    if request.method == "GET":

        offer_id = request.GET.get('offer_id')
        productoffer = Offers.objects.get(id=offer_id)
        change_status = Product.objects.get(id=productoffer.product_id)
        if change_status.is_offer_avail == True:
            change_status.is_offer_avail = False
            change_status.save()
        productoffer.delete()

        return JsonResponse({'msg': 'success', 'message': 'sucessfully deleted'})
    return JsonResponse({'message': 'wrong route'})

#===========================================catrgory offers=======================================

def category_offer(request):
    
    category = Category.objects.all()

    if request.method == 'POST':
        
        try:
            CategoryOffers.objects.get(category_id = request.POST.get('category_name'))
            messages.success(request, 'Offer for this category already exists')
            return redirect('categoryoffer')
        except:
            category_instance = CategoryOffers()
            category_instance.offername = request.POST.get('offername')
            category_instance.category = Category.objects.get(
                id=request.POST.get('category_name'))
            category_instance.dis_percentage = request.POST.get('offer')
            category_instance.enddate = request.POST.get('enddate')
            category_instance.save()

            offer_avail_products = Product.objects.filter(
                    category_id = request.POST.get('category_name'))
            for off in offer_avail_products:
                offers = CategoryOffers.objects.get(category = off.category_id)

                #calculate the discount price.
                product_price = off.price
                savings = (product_price * offers.dis_percentage)/100
                dicounted_price = product_price-savings

                #save the discount price.
                off.category_offer_avail = True
                off.category_offer_price = dicounted_price
                off.save()
            
            messages.success(request, 'Offer added successfully')
            return redirect('categoryoffer')
    else:
        context ={
            'category':category
        }
        return render(request,'admin/categoryoffer.html',context)

def delete_category_offer(request):

    if request.method == "GET":
        offer_id = request.GET.get('offer_id')
        category_offer = CategoryOffers.objects.get(id = offer_id )

        change_statuses = Product.objects.filter(category=category_offer.category_id)
        for change_status in  change_statuses:
            # if change_status.category_offer_avail == True:
            change_status.category_offer_avail = False
            change_status.save()
        category_offer.delete()
        return JsonResponse({'msg': 'success', 'message': 'sucessfully deleted'})
    return JsonResponse({'message': 'wrong route'})

def categoryofferlist(request):
    categoryoffer = CategoryOffers.objects.all()
    return render(request,'admin/categoryoffer-list.html',{'categoryoffer':categoryoffer})


def add_coupon(request):
    if request.method == "POST":
        coupon_instance = CouponOffer()
        coupon_instance.coupon_title = request.POST.get('couponname')
        coupon_instance.coupon_offer = request.POST.get('discountprice')
        coupon_instance.coupon_end = request.POST.get('enddate')
        coupon_instance.coupon_limit = request.POST.get('limit')

        coupon_instance.save()
        return redirect('addcoupon')
    else:
        coupons = CouponOffer.objects.all()
        context = {'coupons':coupons}
        return render(request,'admin/add-coupon.html',context)

def deletecoupon(request):
   
    if request.method == 'GET':
        coupon_id = request.GET.get('coupon_id')
        delete_coupon = CouponOffer.objects.get(id = coupon_id)
        delete_coupon.is_available = False
        delete_coupon.save()
        delete_coupon.delete()

        return JsonResponse({'msg': 'success', 'message': 'sucessfully deleted'})
    return JsonResponse({'message': 'wrong route'})

def admin_banners(request):
    banners = BannerUpdate.objects.all()
    context = {
        'banners': banners,
    }
    return render(request, 'admin/admin_banners.html',context)

def add_banner(request):
    form = BannerUpdateForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('admin_banners')
        else:
            messages.error(request,'form not valid')            
            context = {
            'form':form
            }
            return render(request,'admin/add_banner.html',context)
    else:
        context = {
            'form':form
        }
        return render(request,'admin/add_banner.html',context)
