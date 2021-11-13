from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
   path('',views.adminlogin,name= 'adminlogin'),
   
   path('admindash',views.admindash,name= 'admindash'),
   path('adminbase',views.adminbase,name= 'adminbase'),
   path('adminlogout',views.adminlogout, name= 'adminlogout'),

   path('user/userlist',views.userlist, name ='userlist'),
   path('user/userlist/userblock/<id>',views.userblock, name ='userblock'),


   path('product/productlist',views.productlist, name ='productlist'),
   path('product/addproduct',views.addproduct,name = 'addproduct'),
   path('product/addproduct/editproduct/<id>',views.edit_product,name='editproduct'),
   path('product/addproduct/deleteproduct',views.DeleteProduct,name='deleteproduct'),

   path('category/addcategory',views.addcategory,name = 'addcategory'),
   path('category/categorylist',views.categorylist,name = 'categorylist'),
   path('category/categorylist/editcategory/<id>',views.editCategory,name='editcategory'),
   path('category/categorylist/deletecategory',views.deleteCatergory,name='deletecategory'),

   path('subcategory/subcategorylist',views.SubCategoryList,name = 'subcategorylist'),
   path('subcategory/addsubcategory',views.AddSubCategory,name = 'addsubcategory'),
   path('subcategory/addsubcategory/editsubcatgory/<id>',views.editSubCatergory,name='editsubcatgory'),
   path('subcategory/addsubcategory/deletesubcategory',views.deleteSubCatergory,name='deletesubcategory'),

   path('orders/orders',views.orders,name='orders'),

   path('reports/salesreport',views.salesreport,name='salesreport'),

   path('productoffer',views.productoffer,name='productoffer'),
   path('productofferlist',views.productofferlist,name='productofferlist'),
   path('delete_product_offer',views.delete_product_offer,name='delete_product_offer'),

   path('categoryoffer',views.category_offer,name='categoryoffer'),
   path('categoryofferlist',views.categoryofferlist,name='categoryofferlist'),
   path('deletecategoryoffer',views.delete_category_offer,name='deletecategoryoffer'),

   path('addcoupon',views.add_coupon,name='addcoupon'),
   path('deletecoupon',views.deletecoupon,name='deletecoupon'),

   path('admin_banners',views.admin_banners, name='admin_banners'),    
   path('add_banner',views.add_banner, name='add_banner'),

]