from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from django.contrib import messages
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        # Since we removed categories and approval logic, 
        # we can simplify this or remove it entirely
        if sociallogin.is_existing:
            user = sociallogin.user
            # Check if account is deleted
            if hasattr(user, 'deletion_reason') and user.deletion_reason:
                messages.error(request, f"Your account has been deleted. Reason: {user.deletion_reason}")
                raise ImmediateHttpResponse(redirect('log'))

    def get_login_redirect_url(self, request):
        user = request.user

        # Check if user needs to complete basic profile information
        if not user.phone or not user.name:
            return reverse('sociallog')

        # All users go to home page after social login
        return reverse('home')
