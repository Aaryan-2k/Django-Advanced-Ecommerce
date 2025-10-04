from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

class AccountAdmin(UserAdmin):
    list_display=('username','first_name','last_name','date_joined','last_login', "is_active")
    list_filter=()
    fieldsets=()
    filter_horizontal=()

# Register your models here.
admin.site.register(Account, AccountAdmin)
