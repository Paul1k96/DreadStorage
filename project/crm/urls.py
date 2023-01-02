from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='home'),
    path('detail/<slug:product_slug>/', Detail.as_view(), name='detail'),
    path('detail/<slug:product_slug>/<int:prodinfo_id>/', DetailProdInfoEdit.as_view(), name='edit_prodinfo'),
    path('detail/<slug:product_slug>/<int:prodinfo_id>/delete', DetailProdInfoDelete.as_view(), name='delete_prodinfo'),
    path('detail/<slug:product_slug>/detail_product/', DetailProductEdit.as_view(), name='edit_product'),
    path('detail/<slug:product_slug>/add_prodinfo/', DetailProdInfoAdd.as_view(), name='add_prodinfo_detail'),
    path('add_company/', AddCompany.as_view(), name='add_company'),
    path('add_shop/', AddShop.as_view(), name='add_shop'),
    path('add_newproduct/', AddNewProduct.as_view(), name='add_newproduct'),
    path('add_product/', AddProduct.as_view(), name='add_product'),
    path('ajax/load_objects', load_titles, name='ajax_load_objects'),
    path('login/', LoginUser.as_view(), name='login'),
    path('search_result/', Search.as_view(), name='search_result'),
    path('logout/', logout_user, name='logout'),
    path('registration/', RegUser.as_view(), name='reguser'),
    path("password_reset/", password_reset_request, name='password_reset'),
]