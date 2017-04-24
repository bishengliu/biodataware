from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re


def validate_phone(value):
    """  
    phone_regex = RegexValidator(regex=r'^\+?1?\d{4,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    """

    phone_pattern = re.compile("^\+?1?\d{4,15}$")
    if not phone_pattern.search(value):
        msg = _("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        raise ValidationError(msg)
