from accounts.views import UserRegistrationView,UserLoginView,HomeView,UserLogoutView,UpdateInfoView

from django.urls import path

urlpatterns = [
path('registration/',UserRegistrationView.as_view(),name='register'),
path('login/',UserLoginView.as_view(),name='login'),
path('logout/',UserLogoutView.as_view(),name='logout'),
path('profile/',HomeView.as_view(),name='profile'),
path('Update/',UpdateInfoView.as_view(),name='Update'),
]
