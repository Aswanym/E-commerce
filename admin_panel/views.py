from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from admin_panel.models import Category, Product, SubCategory
from order.models import Order, OrderProduct
import os
# Create your views here.


def adminlogin(request):
    if request.session.has_key('admin_login'):
        return redirect('admindash')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)
            print(user)
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
        return render(request, 'admin/admindash.html')
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

        if len(request.FILES) != 0:
            data.image1 = request.FILES['pic1']
            data.image2 = request.FILES['pic2']
            data.image3 = request.FILES['pic3']
            data.image4 = request.FILES['pic4']

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
    data.category = Category.objects.get(
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

    context = {'data': data

               }
    return render(request, 'admin/product-list.html', context)


def DeleteProduct(request, id):
    data = Product.objects.get(id=id)
    data.delete()
    return redirect('productlist')


#========================================  Category ==============================================#


@login_required(login_url='adminlogin')
def addcategory(request):
    print(request.method)
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

        print('entered')
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

        # messages.success(request,'product added sucessfully')
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
    print(data.id)
    if data.is_active == True:
        data.is_active = False
        data.save()
        return redirect('userlist')
    else:
        data.is_active = True
        data.save()
        return redirect('userlist')

#============================================order===================================

def orders(request):
    order_list = OrderProduct.objects.all()
    context = {
        'order_list' : order_list
    }
    print(context)
    return render(request,'admin/orders.html',context)
