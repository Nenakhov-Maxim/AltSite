"""
URL configuration for AltSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from mainSite import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('robots.txt', views.robots_txt, name='robots-txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('production/', views.products, name='products-base'),
    path('production/<str:prod_type>/', views.products, name='products'),
    path('about/', views.about_us, name='about'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<slug:slug_name>/', views.portfolio, name='portfolio-slug'),
    path('technology/', views.technology, name='technology'),
    path('job/', views.job, name='job'),
    path('job/job-application/', views.jobApplication, name='job-application'),
    path('job/<int:job_id>/', views.job, name='job'),
    path('contacts/', views.contacts, name='contacts'),
    path('captcha/', include('captcha.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('rewards/', views.rewards, name='rewards'),
    path('articles/', views.articles, name='articles'),
    path('articles/<slug:slug_name>/', views.articles, name='article-detail'),
    path('news/', views.news, name='news'),
    path('news/<slug:slug_name>/', views.news, name='news-detail'),
    path('sertificates/', views.sertificates, name='sertificates'),
    path('documents/', views.documents, name='documents'),
    path('facade-system/', views.facadeSystem, name='facadeSystem-base'),
    path('facade-system/<slug:slug_facade_type>/', views.facadeSystem, name='facadeSystem-type'),
    path('facade-system/<slug:slug_facade_type>/<slug:slug_facade_name>/', views.facadeSystem, name='facadeSystem-detail'),

    # Постоянные редиректы с ключевых URL предыдущей версии сайта.
    path('o-kompanii.html', RedirectView.as_view(pattern_name='about', permanent=True)),
    path('portfolio.html', RedirectView.as_view(pattern_name='portfolio', permanent=True)),
    path('kontakty.html', RedirectView.as_view(pattern_name='contacts', permanent=True)),
    path('produkciya.html', RedirectView.as_view(pattern_name='products-base', permanent=True)),
    path(
        'produkciya/klyammery.html',
        RedirectView.as_view(pattern_name='products', permanent=True),
        {'prod_type': 'cladding-mounting'},
    ),
    path(
        'produkciya/fasadnye-kronshtejny.html',
        RedirectView.as_view(pattern_name='products', permanent=True),
        {'prod_type': 'facade-brackets-steel'},
    ),
    path(
        'produkciya/fasadnye-profili.html',
        RedirectView.as_view(pattern_name='products', permanent=True),
        {'prod_type': 'facade-profile-steel'},
    ),
    path('trudoustrojstvo.html', RedirectView.as_view(pattern_name='job', permanent=True)),
    path('fasadnye-sistemy.html', RedirectView.as_view(pattern_name='facadeSystem-base', permanent=True)),
    path(
        'proektirovanie-fasadnyh-sistem.html',
        RedirectView.as_view(pattern_name='technology', permanent=True),
    ),
    path(
        'fasadnye-sistemy/<slug:legacy_type>/<slug:legacy_slug>.html',
        views.legacy_facade_redirect,
        name='legacy-facade-redirect',
    ),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
