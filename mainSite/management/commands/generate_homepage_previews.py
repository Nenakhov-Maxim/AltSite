from django.core.management.base import BaseCommand

from mainSite.image_utils import (
    extract_media_relative_paths_from_html,
    generate_image_variant,
    generate_image_variant_from_name,
)
from mainSite.models import Articles, FacadeSystem, News, Portfolio, PortfolioImage, Product


class Command(BaseCommand):
    help = 'Generate cached preview images for cards, portfolio gallery, and rich text content images.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate previews even if cached files already exist.'
        )

    def handle(self, *args, **options):
        force = options['force']
        total_generated = 0

        jobs = (
            ('FacadeSystem', FacadeSystem.objects.all(), 'main_img', 'facade_system_card'),
            ('Portfolio', Portfolio.objects.all(), 'main_img', 'portfolio_card'),
            ('PortfolioImage gallery', PortfolioImage.objects.all(), 'image_link', 'portfolio_gallery_image'),
            ('PortfolioImage thumb', PortfolioImage.objects.all(), 'image_link', 'portfolio_gallery_thumb'),
            ('Product', Product.objects.all(), 'product_img', 'product_card'),
            ('News', News.objects.all(), 'title_img', 'news_card'),
        )

        for label, queryset, field_name, variant_name in jobs:
            generated_for_model = 0

            for instance in queryset.iterator():
                file_field = getattr(instance, field_name, None)
                relative_name = generate_image_variant(file_field, variant_name, force=force)
                if relative_name:
                    generated_for_model += 1

            total_generated += generated_for_model
            self.stdout.write(f'{label}: {generated_for_model}')

        rich_text_jobs = (
            ('News content', News.objects.all(), 'news_text'),
            ('Articles content', Articles.objects.all(), 'article_text'),
        )

        for label, queryset, field_name in rich_text_jobs:
            generated_for_model = 0
            generated_paths = set()

            for instance in queryset.iterator():
                html = getattr(instance, field_name, '')
                for relative_name in extract_media_relative_paths_from_html(html):
                    if relative_name in generated_paths:
                        continue
                    variant_name = generate_image_variant_from_name(relative_name, 'content_inline', force=force)
                    if variant_name:
                        generated_paths.add(relative_name)
                        generated_for_model += 1

            total_generated += generated_for_model
            self.stdout.write(f'{label}: {generated_for_model}')

        self.stdout.write(self.style.SUCCESS(f'Total previews ready: {total_generated}'))
