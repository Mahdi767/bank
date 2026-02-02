from django.shortcuts import render,redirect
from django.views.generic import FormView, TemplateView,View,UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User


from django.urls import reverse_lazy

from . forms import UserRegistrationForm,UserUpdateForm

# Create your views here.

class UserRegistrationView(FormView):
    template_name = 'accounts/User_reg_form.html'
    success_url = reverse_lazy('profile')
    form_class = UserRegistrationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # print(form.cleaned_data)
        return super().form_valid(form) # sob tik thakle form valid fn call hobe
        

# @method_decorator(ensure_csrf_cookie, name='dispatch')
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('register')
    
class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

@method_decorator(login_required,name= 'dispatch')
class HomeView(TemplateView):
    template_name = 'accounts/profile.html'


@method_decorator(login_required,name='dispatch')
class UpdateInfoView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/update_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        return super().form_valid(form)