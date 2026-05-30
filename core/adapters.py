from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Disables local account registration.
        """
        return False

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """
        Allows registration via social accounts (Cognito).
        """
        return True
