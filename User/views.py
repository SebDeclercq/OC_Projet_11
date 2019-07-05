from typing import Any, Optional
import os
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, View
from .forms import SignUpForm
from .models import User
from .tokens import account_activation_token
from django.contrib.auth.forms import SetPasswordForm


class LoginView(TemplateView):
    template_name: str = 'login.html'

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        email: Optional[str] = request.POST.get('email')
        password: Optional[str] = request.POST.get('password')
        user: Optional[User] = authenticate(  # type: ignore
            username=email, password=password
        )
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/')
        return render(request, self.template_name, {'wrong_credentials': True})


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('/')


class SignUpView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create an inactive user with no password:
            user: User = form.save(commit=False)
            user.is_active = False
            user.set_unusable_password()
            user.save()
            # Send an email to the user with the token:
            mail_subject: str = 'Activate your account.'
            current_site: Any = get_current_site(request)
            uid: bytes = urlsafe_base64_encode(force_bytes(user.pk))
            token: str = account_activation_token.make_token(user)
            activation_link: str = f"http://{current_site}/user/activate/{uid}/{token}"  # noqa
            message: str = f"Hello {user.firstname},\n {activation_link}"
            to_email: str = form.cleaned_data.get('email')
            email: EmailMessage = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse(
                'Please confirm your email address to '
                'complete the registration'
            )
        return HttpResponseBadRequest('Le formulaire est invalide')


class Activate(View):
    def get(
        self, request: HttpRequest, uid: bytes, token: str
    ) -> HttpResponse:
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(
            user, token
        ):
            # activate user and login:
            user.is_active = True
            user.save()
            login(request, user)
            form = SetPasswordForm(request.user)
            return render(request, 'activate.html', {'form': form})

        else:
            return HttpResponse('Activation link is invalid!')

    def post(self, request, *args, **kwargs):
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # Important, to update the session with the new password
            return HttpResponse('Password changed successfully')
        return HttpResponse('Password not set up')


class AccountView(View):
    template_name: str = 'account.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)
