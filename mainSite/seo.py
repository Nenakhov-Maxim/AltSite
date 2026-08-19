from html import unescape
from urllib.parse import urljoin

from django.conf import settings
from django.templatetags.static import static
from django.utils.html import strip_tags


DEFAULT_TITLE = 'Вентилируемые фасады и фасадные системы — ООО «Альтернатива»'
DEFAULT_DESCRIPTION = (
    'Проектирование и производство навесных вентилируемых '
    'фасадов и систем «Альт-Фасад».'
)


def get_site_base_url():
    return getattr(settings, 'SITE_BASE_URL', 'https://alt-ural.ru').rstrip('/')


def _plain_text(value, limit=180):
    text = unescape(strip_tags(value or '')).replace('\xa0', ' ')
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    return f'{text[: limit - 1].rstrip()}…'


def _static_url(path):
    try:
        return static(path)
    except ValueError:
        # An optional SEO image must not make every page fail on a stale manifest.
        return urljoin(settings.STATIC_URL, path)


def build_seo(title=None, description=None, image=None, page_type='website'):
    base_url = get_site_base_url() + '/'
    default_og_image = urljoin(
        base_url,
        _static_url('content/img/background-main.jpg').lstrip('/'),
    )
    image_url = urljoin(base_url, image.lstrip('/')) if image else default_og_image
    return {
        'title': _plain_text(title or DEFAULT_TITLE, 120),
        'description': _plain_text(description or DEFAULT_DESCRIPTION),
        'image': image_url,
        'type': page_type,
    }


def seo_defaults(request):
    return {
        'site_base_url': get_site_base_url(),
        'site_name': getattr(settings, 'SITE_NAME', 'Альтернатива'),
        'seo': build_seo(),
    }
