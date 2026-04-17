from django import template

from mainSite.image_utils import replace_richtext_image_sources


register = template.Library()


@register.filter(name='richtext_image_variants')
def richtext_image_variants(value):
    return replace_richtext_image_sources(value)
