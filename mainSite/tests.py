from django.test import TestCase
from django.urls import reverse

from .models import Articles

class SEOInfrastructureTests(TestCase):
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
            article_text='<p>Как проходят испытания навесных фасадов.</p>',
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
