from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':("product_name",)}
    list_display=("product_name","price","is_available", 'created_at',"modified_at","category")


# Register your models here.
admin.site.register(Product,ProductAdmin)
