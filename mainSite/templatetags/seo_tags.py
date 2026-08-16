from django import template
from django.conf import settings

from mainSite.seo import get_site_base_url


register = template.Library()


@register.simple_tag
def seo_site_base_url():
    return get_site_base_url()


@register.simple_tag
def seo_site_name():
    return getattr(settings, 'SITE_NAME', 'Альтернатива')
