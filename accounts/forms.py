from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserBankAccount,UserBankAddress
from . constant import GENDER_TYPE,ACCOUNT_TYPE
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    country = CountryField().formfield()
    postal_code = forms.IntegerField()
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)

    class Meta:
        model = User
        fields =['username','password1','password2','email','first_name','last_name','account_type','gender','postal_code','country','street_address','city','birth_date']

    def save(self,commit =True):
        our_user = super().save(commit=False)#ami ekhn db te save korbo na
        if commit ==  True:
            our_user.save()
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            street_address = self.cleaned_data.get('street_address')
            city = self.cleaned_data.get('city')
            birth_date = self.cleaned_data.get('birth_date')

            UserBankAddress.objects.create(
                user = our_user,
                  street_address = street_address,
                  country = country,
                  city = city,
                  postal_code = postal_code,
            )
            UserBankAccount.objects.create(
                user = our_user,
                account_type = account_type,
                gender = gender,
                birth_date = birth_date,
                account_no = 100000+our_user.id,
            )
        return our_user


            
class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    country = CountryField().formfield()
    postal_code = forms.IntegerField()
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)

    class Meta:
        model = User
        fields =['first_name','last_name','email']

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill fields if the user already has related records
        if self.instance:
            try:
                user_account = self.instance.accounts
                user_address = self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account and user_address:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self,commit= True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account,created = UserBankAccount.objects.get_or_create(user = user)
            user_address, created = UserBankAddress.objects.get_or_create(user=user)

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user



                     

            

        
