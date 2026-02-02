from django.contrib import admin

# Register your models here.
from .models import UserBankAccount,UserBankAddress
admin.site.register(UserBankAddress)
admin.site.register(UserBankAccount)