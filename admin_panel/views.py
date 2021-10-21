from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.expressions import Window
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.db.models.functions import ExtractMonth
from admin_panel.models import Category, Offers, Product, SubCategory
from order.models import Order, OrderProduct, Payment
import calendar
from django.db.models import Q
import os

from django.core.files.base import ContentFile
import base64

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
        #------------------------------------------------order by month-------------------------------#
        orders = Order.objects.annotate(month=ExtractMonth('created_at')).values(
            'month').annotate(count=Count('id')).values('month', 'count')
        month_number = []
        total_orders = []

        for data in orders:
            month_number.append(calendar.month_name[data['month']])
            total_orders.append(data['count'])
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
    #==================================order details========================================================#
        status = []
        totalcount = []
        orderall = OrderProduct.objects.filter(status__in=('Placed', 'Cancelled', 'Accepted', 'Shipped', 'Ordered')).values(
            'status').annotate(count=Count('status')).values('status', 'count')
        for products in orderall:
            status.append(products['status'])
            totalcount.append(products['count'])
    #===========================================================================================================#
        last_six_order = Order.objects.filter(
            is_ordered=True).order_by('-id')[:6]
        context = {'last_six_order': last_six_order,
                   'month_number': month_number,
                   'total_orders': total_orders,
                   'payment_method': payment_method,
                   'payment_count': payment_count,
                   'stock': stock,
                   'allproduct': allproduct,
                   'status': status,
                   'totalcount': totalcount,
                   'users': users,
                   'user_count': user_count,
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
    if request.method == 'POST':

        data = Product()

        data.product_name = request.POST.get('product_name')
        data.subcategory = SubCategory.objects.get(
            sub_category=request.POST.get('subcategory'))
        data.product_description = request.POST.get('product_description')
        data.product_slug = request.POST.get('product_slug')

        data.price = request.POST.get('price')
        data.stock = request.POST.get('stock')

        image1_base64 = request.POST.get('img1-base64')
        format, img1 = image1_base64.split(';base64,')
        ext = format.split('/')[-1]
        img_data1 = ContentFile(base64.b64decode(img1), name=request.POST.get('product_name') + '1.' + ext)


        image2_base64 = request.POST.get('img2-base64')
        format, img2 = image2_base64.split(';base64,')
        ext = format.split('/')[-1]
        img_data2 = ContentFile(base64.b64decode(img2), name=request.POST.get('product_name') + '2.' + ext)

        # image3_base64 = request.POST.get('img3-base64')
        # format, img3 = image3_base64.split(';base64,')
        # ext = format.split('/')[-1]
        # img_data3 = ContentFile(base64.b64decode(img3), name=request.POST.get('product_name') + '3.' + ext)
       

        # image4_base64 = request.POST.get('img4-base64')
        # format, img4 = image4_base64.split(';base64,')
        # ext = format.split('/')[-1]
        # img_data4 = ContentFile(base64.b64decode(img4), name=request.POST.get('product_name') + '4.' + ext)

        data.image1 = img_data1
        data.image2 = img_data1
        data.image3 = img_data1
        data.image4 = img_data1


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
def EditProduct(request, id):
    product_data = Product.objects.get(id=id)
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()
    context = {
        'category': category,
        'subcategory': subcategory,
        'product_data': product_data
    }
    return render(request, 'admin/edit-product.html', context)


@login_required(login_url='adminlogin')
def EditedProduct(request, id):

    data = Product.objects.get(id=id)
    data.product_name = request.POST.get('product_name')
    data.category = Category.objects.filter(
        category_name=request.POST.get('category'))
    data.product_description = request.POST.get('product_description')
    data.product_slug = request.POST.get('product_slug')

    data.price = request.POST.get('price')
    data.stock = request.POST.get('stock')

    if len(request.FILES) != 0:
        if len(data.image1) > 0:
            os.remove(data.image1.path)
        data.image1 = request.FILES['pic1']
        data.image2 = request.FILES['pic2']
        data.image3 = request.FILES['pic3']
        data.image4 = request.FILES['pic4']

    data.save()
    return redirect('productlist')
    # else:
    #     context = {'data': data}
    #     return render(request,'edit-product.html',context)


@login_required(login_url='/adminlogin/')
def productlist(request):

    data = Product.objects.all()
    context = {'data': data}
    return render(request, 'admin/product-list.html', context)


def DeleteProduct(request, id):
    data = Product.objects.get(id=id)
    data.delete()
    return redirect('productlist')


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
    all_category = Category.objects.all()
    context = {'all_category': all_category}
    return render(request, 'admin/category-list.html', context)


def deleteCatergory(request, id):
    data = Category.objects.get(id=id)
    data.delete()
    return redirect('categorylist')
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

    category = Category.objects.all()
    all_sub_category = SubCategory.objects.all()
    context = {'all_sub_category': all_sub_category,
               'category': category,
               }
    return render(request, 'admin/sub-category-list.html', context)


def deleteSubCatergory(request, id):

    data = SubCategory.objects.get(id=id)
    data.delete()
    return redirect('subcategorylist')


#========================================  user ==============================================#


@login_required(login_url='adminlogin')
def userlist(request):
    data = User.objects.all()
    return render(request, 'admin/userlist.html', {'data': data})


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
    context = {
        'order_list': order_list
    }
    return render(request, 'admin/orders.html', context)

# =======================================sales report====================================


def salesreport(request):

    if request.method == "POST":
        fdate = request.POST['fdate']
        ldate = request.POST['ldate']
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
        data = OrderProduct.objects.filter(~Q(status='Cancelled'))
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
            product_offer.startdate = request.POST.get('startdate')
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
