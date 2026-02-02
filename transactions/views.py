
import datetime
from django.db.models import Sum 
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views import View
from . models import Transaction
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView,ListView
from . constants import DEPOSIT,WITHDRAWAL,LOAN,LOAN_PAID
from . forms import DepositForm,WithdrawForm,LoanRequestForm
from django.core.mail  import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user,amount,subject,templete,type_msg):
    message = render_to_string(
        templete,{
            'user':user,
            'amount' : amount,
             'type_msg': type_msg,
        }
    )

    send_email = EmailMultiAlternatives(subject,'',to=[user.email])
    send_email.attach_alternative(message,'text/html')
    send_email.send()






class TransactionCreateMixin(LoginRequiredMixin,CreateView):
    template_name ='transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
       kwargs =super().get_form_kwargs()
       kwargs.update({
           'account': self.request.user.accounts,
       })
       return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title,
        })
        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Form'

    def get_initial(self):
        initial = {'transaction_type':DEPOSIT}

        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.accounts
        account.balance+=amount
        account.save(
            update_fields =[
                'balance'
            ]
        )
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        send_transaction_email(self.request.user, amount, "Deposit Message", 'transactions/send_mail_user.html','deposit')
        return super().form_valid(form)



class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Form'

    def get_initial(self):
        initial = {'transaction_type':WITHDRAWAL}

        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.accounts
        account.balance-=amount
        account.save(
            update_fields =[
                'balance'
            ]
        )
        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )
        send_transaction_email(self.request.user,amount,"Withdrawal Message ",'transactions/send_mail_user.html','withdraw')
        return super().form_valid(form)
    

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type':LOAN}

        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count =  Transaction.objects.filter(
            account = self.request.user.accounts,transaction_type = 3,loan_approve  = True
        ).count()

        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )

        send_transaction_email(self.request.user,amount,"Loan request ",'transactions/loan_req.html','')
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin,ListView):
    template_name ='transactions/transaction_report.html'
    model = Transaction
    balance = 0 # filter korar age ba pore total amount dekhabo
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.accounts
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str,'%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str,'%Y-%m-%d').date()

            queryset = queryset.filter(timestamp__date__gte = start_date,timestamp__date__lte = end_date)
            self.balance = queryset.aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.accounts.balance
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.accounts
        })
        return context

class PayLoanView(LoginRequiredMixin,View):
    def get(self,request,loan_id):
        loan = get_object_or_404(Transaction,id=loan_id)
        if loan.loan_approve:
            user_account = loan.account

            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request,f"Loan amount is greater thanuser balance")
                return redirect('loan_list')

class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name ='transactions/loan_request.html'
    context_object_name = 'loans'
    def get_queryset(self):
        user_account = self.request.user.accounts
        queryset = Transaction.objects.filter(account = user_account,transaction_type=3)
        return queryset