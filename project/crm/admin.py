from django.contrib import admin

from .models import *


class ProdInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'title', 'company', 'shop', 'cost', 'weight')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'company', 'shop')
    ordering = ('id', 'title')
    list_filter = ('company', 'shop')


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'company')
    list_display_links = ('id', 'company')
    search_fields = ('company',)
    ordering = ('id', 'company')
    prepopulated_fields = {'slug': ('company',)}


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'shop')
    list_display_links = ('id', 'shop')
    search_fields = ('shop',)
    ordering = ('id', 'shop')
    prepopulated_fields = {'slug': ('shop',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'ref_weight', 'photo')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'company')
    ordering = ('id', 'title')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(ProdInfo, ProdInfoAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Product, ProductAdmin)
