import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView

from hyphaeAuth.forms import HyphaeUserCreationForm, HyphaeUserLoginForm
from hyphaeAuth.models import HyphaeUser


class HyphaeSignUpView(CreateView):
    """
    Sign up view.
    """

    form_class = HyphaeUserCreationForm
    success_url = reverse_lazy('core:index')
    template_name = 'hyphaeAuth/authentication/signup.html'
    success_message = 'Successfully created your account.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign up'
        context['description'] = 'Sign up in Hyphae.'
        context['random_image'] = f'hyphae/images/random-bg/{random.randint(0, 47)}.jpg'
        if 'next' in self.request.GET:
            context['next'] = self.request.GET.get('next')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        if 'next' in self.request.GET:
            response = redirect(self.request.GET.get('next'))
        return response


class HyphaeLoginView(SuccessMessageMixin, LoginView):
    """
    Login view.
    """

    authentication_form = HyphaeUserLoginForm
    template_name = 'hyphaeAuth/authentication/login.html'
    success_message = "You're logged in"
    success_url = reverse_lazy('core:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'next' in self.request.GET:
            context['next'] = self.request.GET.get('next')

        context['title'] = 'Compte'
        context['description'] = 'Se connecter à son compte sur Koolapic.'
        context['random_image'] = f'hyphae/images/random-bg/{random.randint(0, 47)}.jpg'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'next' in self.request.GET:
            redirect(self.request.GET.get('next'))
        return response


class HyphaeLogoutView(TemplateView):
    template_name = 'hyphaeAuth/authentication/logout.html'

    def post(self, request):
        logout(request)
        return redirect(reverse_lazy("auth:login"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_image'] = f'hyphae/images/random-bg/{random.randint(0, 47)}.jpg'
        return context


class ProfileView(DetailView):
    model = HyphaeUser
    template_name = 'hyphaeAuth/profile/profile.html'
    context_object_name = 'profile'
    slug_field = 'vanity'
    slug_url_kwarg = 'vanity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.get_object().first_name} {self.get_object().last_name}\'s profile'
        context['description'] = f'View {self.get_object().first_name} {self.get_object().last_name}\'s profile on Hyphae.'
        return context
