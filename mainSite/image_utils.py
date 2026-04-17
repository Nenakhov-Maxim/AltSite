from pathlib import Path

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
    'portfolio_card': {
        'size': (900, 680),
        'quality': 80,
    },
    'news_card': {
        'size': (720, 540),
        'quality': 80,
    },
}

RASTER_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


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


def generate_image_variant(file_field, variant_name, force=False):
    if not file_field or not getattr(file_field, 'name', None) or Image is None:
        return None

    variant_config = HOMEPAGE_IMAGE_VARIANTS.get(variant_name)
    if not variant_config:
        return None

    source_relative_name = Path(file_field.name)
    if source_relative_name.suffix.lower() not in RASTER_EXTENSIONS:
        return None

    media_root = get_media_root()
    source_path = media_root / source_relative_name
    if not source_path.exists():
        return None

    variant_relative_name = get_variant_relative_name(file_field.name, variant_name)
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


def get_image_variant_url(file_field, variant_name):
    if not file_field:
        return ''

    variant_relative_name = generate_image_variant(file_field, variant_name)
    if variant_relative_name:
        return f'{get_media_url()}{variant_relative_name}'

    return getattr(file_field, 'url', '')
