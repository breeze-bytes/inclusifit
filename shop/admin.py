from django.contrib import admin
from .models import Product, ProductSize

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline]

admin.site.register(Product, ProductAdmin)
