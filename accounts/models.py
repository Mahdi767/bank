from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from . constant import ACCOUNT_TYPE,GENDER_TYPE
# Create your models here.
class UserBankAccount(models.Model):
    user = models.OneToOneField(User,related_name='accounts',on_delete=models.CASCADE)
    account_type = models.CharField(choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField()
    gender = models.CharField(choices=GENDER_TYPE)
    initial_deposit_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0,decimal_places=2,max_digits=12)

    def __str__(self):
         return str(self.account_no)

class UserBankAddress(models.Model):
      user = models.OneToOneField(User,related_name='address',on_delete=models.CASCADE)
      street_address = models.CharField(max_length=100)
      city = models.CharField(max_length=100)
      country = CountryField()
      postal_code = models.IntegerField()

      def __str__(self):
         return self.user.email
