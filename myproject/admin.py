from django.contrib import admin
from .models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title',]
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'total', 'created_at']
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']
admin.site.register(OrderItem, OrderItemAdmin)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']
admin.site.register(Wishlist, WishlistAdmin)

class StatusAdmin(admin.ModelAdmin):
    list_display = ['name',]
admin.site.register(Status, StatusAdmin)