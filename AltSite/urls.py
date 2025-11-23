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

from mainSite import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('production/', views.products, name='products'),
    path('production/<str:prod_type>/', views.products, name='products'),
    path('about/', views.about_us, name='about'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<slug:slug_name>/', views.portfolio, name='portfolio'),
    path('technology/', views.technology, name='technology'),
    path('job/', views.job, name='job'),
    path('job/job-application/', views.jobApplication, name='job-application'),
    path('job/<int:job_id>/', views.job, name='job'),
    path('contacts/', views.contacts, name='contacts'),
    path('summernote/', include('django_summernote.urls')),
    path('rewards/', views.rewards, name='rewards'),
    path('articles/', views.articles, name='articles'),
    path('articles/<slug:slug_name>/', views.articles, name='articles'),
    path('news/', views.news, name='news'),
    path('news/<slug:slug_name>/', views.news, name='news'),
    path('sertificates/', views.sertificates, name='sertificates'),
    path('documents/', views.documents, name='documents'),
    path('facade-system/', views.facadeSystem, name='facadeSystem'),
    path('facade-system/<slug:slug_facade_type>/', views.facadeSystem, name='facadeSystem'),
    path('facade-system/<slug:slug_facade_type>/<slug:slug_facade_name>/', views.facadeSystem, name='facadeSystem'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
