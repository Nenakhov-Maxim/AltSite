from io import BytesIO
from unittest.mock import patch

from PIL import Image
from django.test import TestCase, override_settings
from django.urls import reverse
from captcha.models import CaptchaStore

from .forms import ProjectForm
from .models import Articles, Project
from .seo import build_seo
from .static_storage import LenientManifestStaticFilesStorage


class ProjectFormSpamProtectionTests(TestCase):
    def form_data(self, **overrides):
        captcha = CaptchaStore.objects.create(
            challenge='ABCDE',
            response='abcde',
        )
        data = {
            'consumer_name': 'Иван',
            'consumer_email': 'ivan@example.com',
            'consumer_tel': '+79000000000',
            'consumer_message': 'Тестовая заявка',
            'consent_personal_data': 'on',
            'privacy_policy_acknowledged': 'on',
            'website': '',
            'captcha_0': captcha.hashkey,
            'captcha_1': 'ABCDE',
        }
        data.update(overrides)
        return data

    def test_valid_captcha_is_accepted(self):
        form = ProjectForm(self.form_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_honeypot_blocks_submission(self):
        form = ProjectForm(self.form_data(website='https://spam.example'))

        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_contacts_rejects_submission_without_captcha(self):
        data = self.form_data()
        data.pop('captcha_0')
        data.pop('captcha_1')

        response = self.client.post(reverse('contacts'), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введите код с изображения.')
        self.assertFalse(Project.objects.exists())

    def test_contacts_displays_captcha_image(self):
        response = self.client.get(reverse('contacts'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="captcha"')
        self.assertContains(response, '/captcha/image/')

        captcha = CaptchaStore.objects.latest('id')
        image_response = self.client.get(
            reverse('captcha-image', kwargs={'key': captcha.hashkey})
        )
        self.assertEqual(image_response.status_code, 200)
        self.assertEqual(image_response['Content-Type'], 'image/png')
        self.assertEqual(Image.open(BytesIO(image_response.content)).size, (240, 80))

class SEOInfrastructureTests(TestCase):
    def test_static_storage_does_not_crash_on_missing_manifest_entry(self):
        self.assertFalse(LenientManifestStaticFilesStorage.manifest_strict)

    @override_settings(
        SITE_BASE_URL='https://alt-ural.ru',
        STATIC_URL='/AltSite/static/',
    )
    @patch('mainSite.seo.static', side_effect=ValueError('stale manifest'))
    def test_default_seo_image_survives_stale_static_manifest(self, _static):
        seo = build_seo()

        self.assertEqual(
            seo['image'],
            'https://alt-ural.ru/AltSite/static/content/img/background-main.jpg',
        )

    def test_robots_references_production_sitemap(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertContains(response, 'Disallow: /admin/')
        self.assertContains(response, 'Sitemap: https://alt-ural.ru/sitemap.xml')

    def test_key_legacy_urls_redirect_permanently(self):
        redirects = {
            '/o-kompanii.html': '/about/',
            '/portfolio.html': '/portfolio/',
            '/kontakty.html': '/contacts/',
            '/produkciya.html': '/production/',
            '/produkciya/klyammery.html': '/production/cladding-mounting/',
            '/produkciya/fasadnye-kronshtejny.html': '/production/facade-brackets-steel/',
            '/produkciya/fasadnye-profili.html': '/production/facade-profile-steel/',
            '/fasadnye-sistemy.html': '/facade-system/',
            '/proektirovanie-fasadnyh-sistem.html': '/technology/',
            '/trudoustrojstvo.html': '/job/',
        }

        for old_url, new_url in redirects.items():
            with self.subTest(old_url=old_url):
                response = self.client.get(old_url)
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response['Location'], new_url)

    def test_unknown_content_slugs_return_real_404(self):
        urls = (
            '/articles/net-takoy-stati/',
            '/news/net-takoy-novosti/',
            '/facade-system/net-takogo-tipa/',
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                self.assertContains(response, 'noindex,follow', status_code=404)

    def test_article_has_unique_metadata_canonical_and_h1(self):
        article = Articles.objects.create(
            article_title='Испытания фасадных систем',
            article_text=(
                '<h1 class="cms-heading">Внутренний заголовок</h1>'
                '<p>Как&nbsp;проходят испытания навесных фасадов.</p>'
            ),
            slug='ispytaniya-fasadnyh-sistem',
        )

        response = self.client.get(
            reverse('article-detail', kwargs={'slug_name': article.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<title>Испытания фасадных систем — «Альтернатива»</title>', html=True)
        self.assertContains(
            response,
            '<link rel="canonical" href="https://alt-ural.ru/articles/ispytaniya-fasadnyh-sistem/">',
            html=True,
        )
        self.assertContains(response, '<h1 class="news-article-title">Испытания фасадных систем</h1>', html=True)
        self.assertContains(response, '<div class="cms-heading">Внутренний заголовок</div>', html=True)
        self.assertEqual(response.content.count(b'<h1'), 1)
        self.assertNotContains(response, '&amp;nbsp;')

    def test_sitemap_uses_production_domain_and_only_canonical_detail_url(self):
        article = Articles.objects.create(
            article_title='Узлы навесного фасада',
            article_text='Описание узлов.',
            slug='uzly-navesnogo-fasada',
        )

        response = self.client.get('/sitemap.xml')

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'https://alt-ural.ru/articles/{article.slug}/',
        )
        self.assertNotContains(response, 'testserver')
