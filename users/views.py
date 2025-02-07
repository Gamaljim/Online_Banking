from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, login

from django.conf import settings

from .forms import UserRegistrationForm
from .models import CustomUser
from .tokens import account_activation_token

# Create your views here.

class UserRegistrationView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_message = 'Account created successfully. Please check your email to verify your account.'
    success_url = reverse_lazy('activation_pending')

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object
        user.save()

        token = account_activation_token.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        current_site = get_current_site(self.request).domain
        activate_url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
        activate_link = f"http://{current_site}{activate_url}"

        mail_subject = "Activate your account"
        message = render_to_string('users/activate.html', {
            'user': user,
            'activate_link': activate_link
        })

        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Use configured email
            [user.email],
            fail_silently=False,
        )
  

        return response


class ActivationPendingView(TemplateView):
    template_name = 'users/activation_pending.html  '


def activate_account(request, uidb64, token):
    User = get_user_model()

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()

        #loggin the user 
        login(request, user)
        return redirect('home')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


class EditProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    template_name = 'users/edit_profile.html'
    fields = [
        'first_name', 'last_name', 'phone_number',
        'profile_picture', 'address', 'bio'
    ]
    success_message = 'Profile updated successfully'

    def get_object(self, queryset=None):
        return self.request.user
