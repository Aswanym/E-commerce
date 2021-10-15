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
   path('product/addproduct/editproduct/<id>',views.EditProduct,name='editproduct'),
   path('product/addproduct/editedproduct/<id>',views.EditedProduct,name='editedproduct'),
   path('product/addproduct/deleteproduct/<id>',views.DeleteProduct,name='deleteproduct'),

   path('category/addcategory',views.addcategory,name = 'addcategory'),
   path('category/categorylist',views.categorylist,name = 'categorylist'),
   path('category/categorylist/deletecategory/<id>',views.deleteCatergory,name='deletecategory'),

   path('subcategory/subcategorylist',views.SubCategoryList,name = 'subcategorylist'),
   path('subcategory/addsubcategory',views.AddSubCategory,name = 'addsubcategory'),
   path('subcategory/addsubcategory/deletesubcategory/<id>',views.deleteSubCatergory,name='deletesubcategory'),

   path('orders/orders',views.orders,name='orders'),

   path('reports/salesreport',views.salesreport,name='salesreport'),

   path('productoffer',views.productoffer,name='productoffer'),
   path('productofferlist',views.productofferlist,name='productofferlist'),
   path('delete_product_offer',views.delete_product_offer,name='delete_product_offer'),

]