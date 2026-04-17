from difflib import SequenceMatcher
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from unidecode import unidecode

from mainSite.image_utils import HOMEPAGE_IMAGE_VARIANTS, media_file_exists
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

    def add_arguments(self, parser):
        parser.add_argument(
            '--suggest',
            action='store_true',
            help='Show likely replacement files from media for each broken reference.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=3,
            help='How many candidate replacement files to print for each broken reference.',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Replace broken DB paths with the best candidate when its score is high enough.',
        )
        parser.add_argument(
            '--min-score',
            type=float,
            default=1.15,
            help='Minimum match score required for automatic replacement when using --apply.',
        )

    def handle(self, *args, **options):
        suggest = options['suggest'] or options['apply']
        apply_changes = options['apply']
        limit = max(options['limit'], 1)
        min_score = options['min_score']
        media_files = self._collect_media_files() if suggest else None

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
        replaced_total = 0

        for model_label, queryset, field_name, title_field in checks:
            model_broken = 0
            model_replaced = 0

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
                if suggest:
                    suggestions = self._suggest_replacements(file_field.name, media_files, limit)
                    if apply_changes and suggestions:
                        best_path, best_score = suggestions[0]
                        if best_score >= min_score:
                            self._replace_file_path(instance, field_name, best_path)
                            model_replaced += 1
                            replaced_total += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  -> replaced with: "{best_path}" (score: {best_score:.2f})'
                                )
                            )
                            continue

                    if suggestions:
                        for suggested_path, score in suggestions:
                            self.stdout.write(f'  -> maybe: "{suggested_path}" (score: {score:.2f})')
                    else:
                        self.stdout.write('  -> maybe: no similar file found')

            self.stdout.write(f'{model_label} broken refs: {model_broken}')
            if apply_changes:
                self.stdout.write(self.style.SUCCESS(f'{model_label} replaced refs: {model_replaced}'))

        if broken_total:
            self.stdout.write(self.style.WARNING(f'Total broken refs: {broken_total}'))
        else:
            self.stdout.write(self.style.SUCCESS('No broken image refs found.'))

        if apply_changes:
            self.stdout.write(self.style.SUCCESS(f'Total replaced refs: {replaced_total}'))

    def _collect_media_files(self):
        media_root = Path('media')
        if not media_root.exists():
            return []
        preview_suffixes = tuple(f'__{name}' for name in HOMEPAGE_IMAGE_VARIANTS)
        return [
            path.relative_to(media_root).as_posix()
            for path in media_root.rglob('*')
            if path.is_file()
            and not any(path.stem.endswith(suffix) for suffix in preview_suffixes)
        ]

    def _normalize_name(self, value):
        path = Path(value)
        stem = unidecode(path.stem).lower()
        if '_' in stem:
            head, tail = stem.rsplit('_', 1)
            if len(tail) in (7, 8) and tail.isalnum():
                stem = head
        normalized = ''.join(char for char in stem if char.isalnum())
        return normalized

    def _score_candidate(self, missing_path, candidate_path):
        missing = Path(missing_path)
        candidate = Path(candidate_path)

        missing_dir = missing.parent.as_posix()
        candidate_dir = candidate.parent.as_posix()
        missing_name = self._normalize_name(missing_path)
        candidate_name = self._normalize_name(candidate_path)

        score = SequenceMatcher(None, missing_name, candidate_name).ratio()

        if missing_dir and missing_dir == candidate_dir:
            score += 0.35
        elif missing.parts[:1] and candidate.parts[:1] and missing.parts[0] == candidate.parts[0]:
            score += 0.15

        if missing.suffix.lower() == candidate.suffix.lower():
            score += 0.05

        return score

    def _suggest_replacements(self, missing_path, media_files, limit):
        missing = Path(missing_path)
        same_dir_candidates = []
        fallback_candidates = []

        for media_path in media_files:
            candidate = Path(media_path)
            if candidate.parent == missing.parent:
                same_dir_candidates.append(media_path)
            elif missing.parts[:1] and candidate.parts[:1] and missing.parts[0] == candidate.parts[0]:
                fallback_candidates.append(media_path)

        candidates = same_dir_candidates or fallback_candidates or media_files
        ranked = sorted(
            ((candidate, self._score_candidate(missing_path, candidate)) for candidate in candidates),
            key=lambda item: item[1],
            reverse=True,
        )

        best = []
        seen = set()
        for candidate, score in ranked:
            if candidate in seen or score <= 0.25:
                continue
            seen.add(candidate)
            best.append((candidate, score))
            if len(best) >= limit:
                break

        return best

    @transaction.atomic
    def _replace_file_path(self, instance, field_name, new_path):
        file_field = getattr(instance, field_name)
        file_field.name = new_path
        instance.save(update_fields=[field_name])
