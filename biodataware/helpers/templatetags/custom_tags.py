# https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/
from django import template
from django.conf import settings
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def app_setting_mode():
    if settings.APP_MODE == "local":
        return "local"
    elif settings.APP_MODE == "test":
        return "test"
    else:
        return "production"


@register.simple_tag
def app_name():
    return settings.APP_NAME


@register.simple_tag
def app_version():
    return settings.APP_VERSION


# GET navbar based on app mode
@register.simple_tag
def app_navbar():
    if settings.APP_MODE == "local":
        return render_to_string("navbar_local.html")
    elif settings.APP_MODE == "test":
        return render_to_string("navbar_test.html")
    else:
        return render_to_string("navbar_prod.html")
