from django.core.management.base import BaseCommand

from mainSite.image_utils import generate_image_variant
from mainSite.models import FacadeSystem, News, Portfolio, PortfolioImage


class Command(BaseCommand):
    help = 'Generate cached preview images for homepage cards and portfolio gallery.'

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

        self.stdout.write(self.style.SUCCESS(f'Total previews ready: {total_generated}'))
