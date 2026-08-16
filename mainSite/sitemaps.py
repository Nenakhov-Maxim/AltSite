from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Articles, FacadeSystem, FacadeSystemBase, News, Portfolio, ProductType


class StaticSitemap(Sitemap):
    protocol = 'https'
    priority = 0.6
    changefreq = 'monthly'

    route_names = (
        'index',
        'about',
        'portfolio',
        'technology',
        'job',
        'contacts',
        'rewards',
        'articles',
        'news',
        'sertificates',
        'documents',
        'facadeSystem-base',
        'products-base',
    )

    def items(self):
        return self.route_names

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'index' else 0.6


class ProductTypeSitemap(Sitemap):
    protocol = 'https'
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return ProductType.objects.exclude(product_link__isnull=True).exclude(product_link='').order_by('pk')

    def location(self, item):
        return reverse('products', kwargs={'prod_type': item.product_link})


class PortfolioSitemap(Sitemap):
    protocol = 'https'
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return Portfolio.objects.exclude(slug='').order_by('pk')

    def location(self, item):
        return reverse('portfolio-slug', kwargs={'slug_name': item.slug})


class ArticleSitemap(Sitemap):
    protocol = 'https'
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return Articles.objects.exclude(slug='').order_by('-created_at')

    def location(self, item):
        return reverse('article-detail', kwargs={'slug_name': item.slug})

    def lastmod(self, item):
        return item.created_at


class NewsSitemap(Sitemap):
    protocol = 'https'
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return News.objects.exclude(slug='').order_by('-created_at')

    def location(self, item):
        return reverse('news-detail', kwargs={'slug_name': item.slug})

    def lastmod(self, item):
        return item.created_at


class FacadeTypeSitemap(Sitemap):
    protocol = 'https'
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return FacadeSystemBase.objects.exclude(facade_base_slug='').order_by('pk')

    def location(self, item):
        return reverse('facadeSystem-type', kwargs={'slug_facade_type': item.facade_base_slug})


class FacadeSystemSitemap(Sitemap):
    protocol = 'https'
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return FacadeSystem.objects.select_related('fs_type').exclude(fs_slug='').order_by('pk')

    def location(self, item):
        return reverse(
            'facadeSystem-detail',
            kwargs={
                'slug_facade_type': item.fs_type.facade_base_slug,
                'slug_facade_name': item.fs_slug,
            },
        )


sitemaps = {
    'static': StaticSitemap,
    'product-types': ProductTypeSitemap,
    'portfolio': PortfolioSitemap,
    'articles': ArticleSitemap,
    'news': NewsSitemap,
    'facade-types': FacadeTypeSitemap,
    'facade-systems': FacadeSystemSitemap,
}
