from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_score(value):
    if 1 <= value <= 10:
        return value
    raise ValidationError(
        _('%(value)s is not in range 1..10.'), params={'value': value}, )
