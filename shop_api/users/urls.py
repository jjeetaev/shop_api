from django.urls import path
from .views import RegistrationView, LoginView, ConfirmationView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('confirm/', ConfirmationView.as_view(), name='confirm'),
]
