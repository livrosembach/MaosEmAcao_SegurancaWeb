from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Desabilita cadastro local
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        # Permite login pelo Cognito
        return True

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Associa automaticamente a conta Cognito ao usuário Django existente.
        """
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email

        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass