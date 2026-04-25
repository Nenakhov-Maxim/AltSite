from pathlib import Path
import re
from urllib.parse import unquote, urlparse

from django.conf import settings
from unidecode import unidecode

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
except ImportError:
    Image = None
    ImageOps = None
    UnidentifiedImageError = Exception


HOMEPAGE_IMAGE_VARIANTS = {
    'facade_system_card': {
        'size': (960, 720),
        'quality': 80,
    },
    'content_inline': {
        'size': (1440, 1440),
        'quality': 82,
    },
    'portfolio_card': {
        'size': (900, 680),
        'quality': 80,
    },
    'portfolio_gallery_image': {
        'size': (1800, 1350),
        'quality': 82,
    },
    'portfolio_gallery_thumb': {
        'size': (420, 315),
        'quality': 78,
    },
    'portfolio_subsystem_image': {
        'size': (1280, 960),
        'quality': 82,
    },
    'portfolio_subsystem_thumb': {
        'size': (640, 480),
        'quality': 80,
    },
    'portfolio_cladding_image': {
        'size': (1280, 960),
        'quality': 82,
    },
    'portfolio_cladding_thumb': {
        'size': (480, 360),
        'quality': 78,
    },
    'product_card': {
        'size': (720, 720),
        'quality': 80,
    },
    'news_card': {
        'size': (720, 540),
        'quality': 80,
    },
}

RASTER_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
IMG_SRC_RE = re.compile(r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])([^"\']+)(\2)', re.IGNORECASE)
EMPTY_IMAGE_PLACEHOLDER = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 3'>"
    "<rect width='4' height='3' fill='%23e5e7eb'/>"
    "</svg>"
)


def get_media_root():
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.is_absolute():
        media_root = Path(settings.BASE_DIR) / media_root
    return media_root


def get_media_url():
    media_url = settings.MEDIA_URL
    if not media_url.startswith('/'):
        media_url = f'/{media_url}'
    if not media_url.endswith('/'):
        media_url = f'{media_url}/'
    return media_url


def sanitize_variant_stem(stem):
    ascii_stem = unidecode(stem)
    ascii_stem = ''.join(char for char in ascii_stem if char.isalnum() or char in ('-', '_'))
    return ascii_stem[:100] or 'image'


def get_variant_relative_name(file_name, variant_name):
    original_path = Path(file_name)
    sanitized_stem = sanitize_variant_stem(original_path.stem)
    return original_path.with_name(f'{sanitized_stem}__{variant_name}.webp').as_posix()


def media_file_exists(file_name):
    if not file_name:
        return False

    media_root = get_media_root()
    return (media_root / Path(file_name)).exists()


def get_media_relative_name_from_url(url):
    if not url:
        return None

    parsed = urlparse(url)
    path = unquote(parsed.path or url).strip()
    if not path:
        return None

    media_variants = {
        get_media_url().rstrip('/'),
        settings.MEDIA_URL.rstrip('/'),
        f'/{settings.MEDIA_URL.strip("/")}',
    }

    for media_prefix in media_variants:
        normalized_prefix = media_prefix.rstrip('/')
        if normalized_prefix and path.startswith(f'{normalized_prefix}/'):
            return path[len(normalized_prefix):].lstrip('/')

    return None


def generate_image_variant_from_name(file_name, variant_name, force=False):
    if not file_name or Image is None:
        return None

    variant_config = HOMEPAGE_IMAGE_VARIANTS.get(variant_name)
    if not variant_config:
        return None

    source_relative_name = Path(file_name)
    if source_relative_name.suffix.lower() not in RASTER_EXTENSIONS:
        return None

    media_root = get_media_root()
    source_path = media_root / source_relative_name
    if not source_path.exists():
        return None

    variant_relative_name = get_variant_relative_name(file_name, variant_name)
    variant_path = media_root / variant_relative_name

    if (
        not force
        and variant_path.exists()
        and variant_path.stat().st_mtime >= source_path.stat().st_mtime
    ):
        return variant_relative_name

    variant_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(source_path) as image:
            image = ImageOps.exif_transpose(image)
            image.thumbnail(variant_config['size'], Image.Resampling.LANCZOS)

            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')

            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, '#ffffff')
                background.paste(image, mask=image.getchannel('A'))
                image = background
            else:
                image = image.convert('RGB')

            image.save(
                variant_path,
                format='WEBP',
                quality=variant_config['quality'],
                optimize=True,
                method=6
            )
    except (OSError, ValueError, UnidentifiedImageError):
        return None

    return variant_relative_name


def generate_image_variant(file_field, variant_name, force=False):
    if not file_field or not getattr(file_field, 'name', None):
        return None

    return generate_image_variant_from_name(file_field.name, variant_name, force=force)


def get_image_variant_url(file_field, variant_name):
    if not file_field:
        return EMPTY_IMAGE_PLACEHOLDER

    variant_relative_name = generate_image_variant(file_field, variant_name)
    if variant_relative_name:
        return f'{get_media_url()}{variant_relative_name}'

    if getattr(file_field, 'name', None) and media_file_exists(file_field.name):
        return getattr(file_field, 'url', EMPTY_IMAGE_PLACEHOLDER)

    return EMPTY_IMAGE_PLACEHOLDER


def get_image_variant_url_from_name(file_name, variant_name):
    if not file_name:
        return EMPTY_IMAGE_PLACEHOLDER

    variant_relative_name = generate_image_variant_from_name(file_name, variant_name)
    if variant_relative_name:
        return f'{get_media_url()}{variant_relative_name}'

    if media_file_exists(file_name):
        return f'{get_media_url()}{Path(file_name).as_posix()}'

    return EMPTY_IMAGE_PLACEHOLDER


def get_image_variant_url_from_src(src, variant_name):
    file_name = get_media_relative_name_from_url(src)
    if not file_name:
        return src

    variant_relative_name = generate_image_variant_from_name(file_name, variant_name)
    if variant_relative_name:
        return f'{get_media_url()}{variant_relative_name}'

    if media_file_exists(file_name):
        return src

    return EMPTY_IMAGE_PLACEHOLDER


def replace_richtext_image_sources(html, variant_name='content_inline'):
    if not html:
        return html

    def replace_match(match):
        prefix, quote, src, _ = match.groups()
        variant_src = get_image_variant_url_from_src(src, variant_name)
        return f'{prefix}{quote}{variant_src}{quote}'

    return IMG_SRC_RE.sub(replace_match, html)


def extract_media_relative_paths_from_html(html):
    if not html:
        return []

    paths = []
    seen = set()
    for match in IMG_SRC_RE.finditer(html):
        relative_name = get_media_relative_name_from_url(match.group(3))
        if not relative_name or relative_name in seen:
            continue
        seen.add(relative_name)
        paths.append(relative_name)

    return paths
