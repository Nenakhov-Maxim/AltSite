import re

from django import template

from mainSite.image_utils import replace_richtext_image_sources


register = template.Library()

H1_TAG_RE = re.compile(r'<(?P<closing>/?)h1(?P<attrs>\s[^>]*)?>', re.IGNORECASE)


def replace_embedded_h1(value):
    """Keep the page title as the only H1 when rich text comes from the CMS."""
    if not value:
        return value

    def replace_tag(match):
        closing = match.group('closing')
        attrs = '' if closing else (match.group('attrs') or '')
        return f'<{closing}div{attrs}>'

    return H1_TAG_RE.sub(replace_tag, value)


@register.filter(name='richtext_image_variants')
def richtext_image_variants(value):
    value = replace_richtext_image_sources(value)
    return replace_embedded_h1(value)
