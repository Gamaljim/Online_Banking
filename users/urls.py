from django.urls import path, include
from .views import UserRegistrationView, EditProfileView, ActivationPendingView , activate_account

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('activation-pending/', ActivationPendingView.as_view(), name='activation_pending'),
    
    path('activate/<str:uidb64>/<str:token>/', activate_account, name='activate'),
]