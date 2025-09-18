from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver

@receiver(social_account_added)
@receiver(social_account_updated)
def populate_user_from_google(request, sociallogin, **kwargs):
    user = sociallogin.user
    extra_data = sociallogin.account.extra_data

    user.first_name = extra_data.get('given_name', '')
    user.last_name = extra_data.get('family_name', '')
    if not user.created_at:
        from django.utils import timezone
        user.created_at = timezone.now()
    user.save()
