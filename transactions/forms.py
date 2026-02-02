from django import forms
from . models import Transaction
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
    
    def __init__(self,*args, **kwargs):
        self.user_account = kwargs.pop('account')
        super().__init__(*args,**kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.user_account
        self.instance.balance_after_transaction = self.user_account.balance
        return super().save()
    

class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit = 100
        amount = self.cleaned_data.get('amount')## user er fill up kora form theke amra amount field er value ke niye aslam,

        if amount < min_deposit:
            raise forms.ValidationError(
                f'You have to deposit at least {min_deposit}$'
            )
        return amount
        

class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.user_account
        min_withdraw = 200
        max_withdraw = 10000
        amount = self.cleaned_data.get('amount')
        balance = account.balance

        if amount < min_withdraw:
            raise forms.ValidationError(
                 f'You can withdraw at most {max_withdraw} $'
            )
        
        if amount > max_withdraw:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw} $'
            )
        
        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
    

        return amount