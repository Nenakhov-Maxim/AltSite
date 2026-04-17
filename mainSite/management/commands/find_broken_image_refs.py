from django.core.management.base import BaseCommand

from mainSite.image_utils import media_file_exists
from mainSite.models import (
    Documents,
    FacadeSystem,
    News,
    Portfolio,
    PortfolioImage,
    Product,
    Rewards,
    Sertificate,
)


class Command(BaseCommand):
    help = 'Find database image/file references that point to missing files in media.'

    def handle(self, *args, **options):
        checks = (
            ('Product', Product.objects.all(), 'product_img', 'product_name'),
            ('Portfolio', Portfolio.objects.all(), 'main_img', 'title'),
            ('PortfolioImage', PortfolioImage.objects.all(), 'image_link', 'alt'),
            ('Rewards', Rewards.objects.all(), 'reward_img', 'reward_title'),
            ('News', News.objects.all(), 'title_img', 'news_title'),
            ('Sertificate', Sertificate.objects.all(), 'sert_img', 'sert_title'),
            ('Documents', Documents.objects.all(), 'doc_img', 'doc_title'),
            ('FacadeSystem', FacadeSystem.objects.all(), 'main_img', 'fs_name'),
        )

        broken_total = 0

        for model_label, queryset, field_name, title_field in checks:
            model_broken = 0

            for instance in queryset.iterator():
                file_field = getattr(instance, field_name, None)
                if not file_field or not getattr(file_field, 'name', None):
                    continue

                if media_file_exists(file_field.name):
                    continue

                model_broken += 1
                broken_total += 1
                title = getattr(instance, title_field, '')
                self.stdout.write(
                    f'{model_label}: id={instance.pk}, title="{title}", field={field_name}, path="{file_field.name}"'
                )

            self.stdout.write(f'{model_label} broken refs: {model_broken}')

        if broken_total:
            self.stdout.write(self.style.WARNING(f'Total broken refs: {broken_total}'))
        else:
            self.stdout.write(self.style.SUCCESS('No broken image refs found.'))
