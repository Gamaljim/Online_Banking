from django.urls import include, path

from .views import (
    ActivationPendingView,
    EditProfileView,
    UserRegistrationView,
    activate_account,
)

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("edit-profile/", EditProfileView.as_view(), name="edit_profile"),
    path(
        "activation-pending/",
        ActivationPendingView.as_view(),
        name="activation_pending",
    ),
    path("activate/<str:uidb64>/<str:token>/", activate_account, name="activate"),
]
