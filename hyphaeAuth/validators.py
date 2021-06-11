from django.core.exceptions import ValidationError

from hyphaeAuth.models import HyphaeUser


def validate_user_email(value):
    if HyphaeUser.objects.filter(email=value).exists():
        raise ValidationError("This email adress is already used.")
