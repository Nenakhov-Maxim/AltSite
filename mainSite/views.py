import json
from types import SimpleNamespace
from urllib.parse import urlparse

from django.http import Http404, HttpResponse, JsonResponse
from django.db.models import F, Prefetch
from django.db.models.functions import Lower, Trim
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .image_utils import get_existing_image_variant_url
from .sendMail import SendEmail
from .forms import ProjectForm
from .privacy import PRIVACY_POLICY_VERSION
from .seo import build_seo, get_site_base_url
from .sitemaps import sitemaps


def robots_txt(request):
    content = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /accounts/',
        'Disallow: /summernote/',
        f'Sitemap: {get_site_base_url()}/sitemap.xml',
        '',
    ])
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def sitemap_xml(request):
    domain = urlparse(get_site_base_url()).netloc
    site = SimpleNamespace(domain=domain)
    urlset = []
    for sitemap_class in sitemaps.values():
        urlset.extend(sitemap_class().get_urls(site=site, protocol='https'))
    return TemplateResponse(
        request,
        'sitemap.xml',
        {'urlset': urlset},
        content_type='application/xml',
    )


# Представление страниц
# Главная страница
def index(request):
    uuid = 'index'
    title_content = PageContent.objects.get(page_uuid=uuid)
    geo_content = list(
        GeographicalPresence.objects.filter(visible_on_map=True).prefetch_related(
            Prefetch(
                'adresses',
                queryset=RegionAdress.objects.filter(visible_on_site=True).order_by('id'),
                to_attr='visible_addresses'
            ),
            'linked_regions'
        ).order_by('region_name')
    )
    geo_map_config = {
        'regionLinks': {
            region.region_code: sorted({
                linked_region.region_code
                for linked_region in region.linked_regions.all()
                if linked_region.region_code
            })
            for region in geo_content
        },
        'cityMarkers': [
            {
                'code': region.region_code,
                'label': region.city_name.strip(),
                'x': region.city_x,
                'y': region.city_y,
                'offsetX': region.city_offset_x,
                'offsetY': region.city_offset_y
            }
            for region in geo_content
            if region.show_city_label and region.city_name.strip()
        ],
        'titlesByCode': {
            region.region_code: region.region_name
            for region in geo_content
        }
    }
    product_content = ProductionBase.objects.all().order_by('position')
    portfolio_lib = Portfolio.objects.all()
    news_lib = News.objects.all().order_by('-created_at')[0:10]
    fs_system = FacadeSystem.objects.filter(display_in_main=True)
    data = {
        'title_content' : title_content,
        'geo_content' : geo_content,
        'geo_map_config': geo_map_config,
        'product_content' : product_content,
        'portfolio_lib': portfolio_lib,
        'news_lib': news_lib,
        'fs_system': fs_system,
        'seo': build_seo(),
    }
    
    return render(request,'main.html', data)

def products(request, prod_type = 'all'):
    
    if prod_type == 'all':
        products_library = Product.objects.select_related('product_type').order_by(
            F('product_type__sort_order').asc(nulls_last=True),
            Lower(Trim('product_type__product_type')),
            F('sort_order').asc(nulls_last=True),
            Lower(Trim("product_name")),
            "product_name",
        )
        bread_crumbs = {
            '/': 'Главная',
            '/production/': 'Комплектующие для фасадных систем',
        } 
        page_title = 'Комплектующие для фасадных систем — производство и поставка'
        page_description = (
            'Комплектующие для навесных вентилируемых фасадов: кронштейны, '
            'профили и элементы крепления производства «Альтернатива».'
        )
    
    else:
        product_type = get_object_or_404(ProductType, product_link=prod_type)
        products_library = Product.objects.filter(product_type=product_type).order_by(
            F('sort_order').asc(nulls_last=True),
            Lower(Trim("product_name")),
            "product_name",
        )
            
        bread_crumbs = {
            '/': 'Главная',
            '/production/': 'Продукция',
            f'/production/{prod_type}/': f'{product_type.product_type}'
        }
        page_title = f'{product_type.product_type} для вентфасадов — «Альтернатива»'
        page_description = (
            f'{product_type.product_type}: производство и поставка комплектующих '
            'для навесных вентилируемых фасадов.'
        )
    
    data = {
        'products': products_library,
        'bread_crumbs': bread_crumbs,
        'page_title': page_title,
        'seo': build_seo(page_title, page_description),
    }
    
    return render(request, 'production.html', data)

# Страница "О нас"
def about_us(request):
    bread_crumbs = {
            '/': 'Главная',
            '/about/': 'О компании',
        }
    data = {
        'content': AboutUs.objects.last(),
        'bread_crumbs': bread_crumbs,
        'seo': build_seo(
            'О компании «Альтернатива» — производство фасадных систем',
            'Завод «Альтернатива»: проектирование и производство навесных '
            'вентилируемых фасадных систем с 2003 года.',
        ),
        }
    return render(request, 'about.html', data)

# Страница "Портфолио"
def portfolio(request, slug_name=None):
    if request.method == 'GET':
        if not slug_name:
            portfolio_lib = Portfolio.objects.prefetch_related(
                'cladding_systems',
                'facade_systems',
            ).all()
            cladding_array = {}
            type_objects_array = []
            region_array = []
            city_array = []
            for portfolio in portfolio_lib:
                if portfolio.object_type:
                    type_objects_array.append(portfolio.object_type)
                
                if portfolio.region:
                    region_array.append(portfolio.region)
                
                if portfolio.city:
                    city_array.append(portfolio.city)
                
                cladding_list = portfolio.getAllCladdingSystem()
                if (cladding_list):
                    for cladding in cladding_list:
                        cladding_array[cladding.id] = cladding.cladding_name
                

            data = {
                'portfolio_lib': portfolio_lib,
                'cladding_array': cladding_array,
                'type_objects_array': type_objects_array,
                'region_array': region_array,
                'city_array': city_array,
                'seo': build_seo(
                    'Проекты вентилируемых фасадов — портфолио «Альтернатива»',
                    'Реализованные объекты с фасадными системами «Альт-Фасад»: '
                    'жилые, общественные и коммерческие здания.',
                )
            }
            return render(request, 'portfolio.html', data)
        else:
            project = Portfolio.objects.prefetch_related(
                Prefetch(
                    'images',
                    queryset=PortfolioImage.objects.only('id', 'alt', 'image_link', 'portfolio_id')
                ),
                Prefetch(
                    'cladding_systems',
                    queryset=claddingSystemPortfolio.objects.only(
                        'id',
                        'cladding_name',
                        'square',
                        'portfolio_id'
                    )
                ),
                Prefetch(
                    'facade_systems',
                    queryset=FacadeSystem.objects.select_related('fs_type').only(
                        'id',
                        'fs_name',
                        'prev_text',
                        'fs_slug',
                        'main_img',
                        'fs_type_id',
                        'fs_type__facade_base_slug'
                    )
                ),
            ).only(
                'id',
                'title',
                'slug',
                'main_img',
                'city',
                'customer',
                'architect',
                'installer',
                'year_comlited',
            ).filter(slug=slug_name).first()
            if project:
                portfolio_images = list(project.images.all())
                cladding_objects = list(project.cladding_systems.all())
                facade_systems = list(project.facade_systems.all())

                gallery_array = [
                    {
                        'image_url': get_existing_image_variant_url(image.image_link, 'portfolio_gallery_image'),
                        'thumb_url': get_existing_image_variant_url(image.image_link, 'portfolio_gallery_thumb'),
                        'alt': image.alt,
                    }
                    for image in portfolio_images
                ]
                cladding_array = [cladding.cladding_name for cladding in cladding_objects]
                total_square = round(sum(cladding.square or 0 for cladding in cladding_objects), 2)
                facade_system_cards = [
                    {
                        'name': system.fs_name,
                        'preview_text': system.prev_text,
                        'image_url': get_existing_image_variant_url(system.main_img, 'portfolio_subsystem_image'),
                        'link': f'/facade-system/{system.fs_type.facade_base_slug}/{system.fs_slug}/',
                    }
                    for system in facade_systems
                ]

                project_image_url = get_existing_image_variant_url(project.main_img, 'portfolio_card')
                data = {
                    'bread_crumbs': {
                        project.title: f'/portfolio/{project.slug}/'
                    },
                    'portfolio_title': project.title,
                    'project': project,
                    'project_image_url': project_image_url,
                    'gallery_array': gallery_array,
                    'cladding_array': cladding_array,
                    'total_square': total_square,
                    'facade_system_cards': facade_system_cards,
                    'seo': build_seo(
                        f'{project.title} — фасадные решения и характеристики',
                        f'{project.title}: примененные фасадные системы, облицовка, '
                        f'площадь и участники проекта. {project.city or ""}',
                        project_image_url,
                    ),
                }
                return render(request, 'portfolio-project.html', data)
            raise Http404
            
    else:
        raise Http404 
    

# Страница "Технологии"
def technology(request):
    content = TechnologyPageContent.objects.last()
    data = {
        'title': 'Технологии',
        'content': content,
        'seo': build_seo(
            'Проектирование фасадных систем — «Альтернатива»',
            'Проектирование навесных вентилируемых фасадов, расчеты, '
            'конструкторская документация и комплектация объекта.',
        ),
    }
    return render(request, 'services.html', data)

# Страница "Вакансии"
def job(request, job_id=None):
    if request.method == 'GET':
        content = VacanciesPageContent.objects.all()
        vacancies = Vacancies.objects.filter(isActive=True).order_by('created_at')
        data = {
            'content': content,
            'vacancies': vacancies,
            'seo': build_seo(
                'Вакансии завода «Альтернатива»',
                'Актуальные вакансии компании «Альтернатива», условия работы и форма отклика.',
            ),
        }
        return render(request, 'job.html', data)
    elif request.method == 'POST':
        job = Vacancies.objects.get(id=job_id)
        job_content = {
            'id': job.id,
            'title': job.title,
            'region': job.region,
            'responsibilities': job.responsibilities
        }
        if job:
            return JsonResponse({'success': True, 'data': job_content})
        else:
            return JsonResponse({'success': False, 'error': 'Запись не найдена'})
    else:
        return JsonResponse({'success': False, 'error': 'Недопустимый метод'}, status=405)

# Отклик на вакансию

def jobApplication(request):
    if request.method == 'POST':
        personal_data_consent = request.POST.get('respond-vacancy-personal-info-approve') == 'on'
        privacy_policy_acknowledged = request.POST.get('respond-vacancy-privacy-policy-acknowledged') == 'on'
        if not personal_data_consent or not privacy_policy_acknowledged:
            return JsonResponse({
                'success': False,
                'error': 'Необходимо дать согласие и ознакомиться с политикой',
            }, status=400)

        if request.FILES:
            resume_file = request.FILES['respond-vacancy-file-upload']
        else:
            resume_file = None
        try:
            new_candidate = VacanciesApplication.objects.create(
                job_id=request.POST.get('vacancies-id'),
                candidate_name=request.POST.get('respond-vacancy-username'),
                candidate_birthday=request.POST.get('respond-vacancy-birthday'),
                candidate_adress=request.POST.get('respond-vacancy-adress'),
                candidate_education_level=request.POST.get('respond-vacancy-education-level'),
                candidate_subeducation_level=request.POST.get('respond-vacancy-subeducation-level'),
                candidate_marital_status=request.POST.get('respond-vacancy-marital-status'), 
                candidate_desire_income=request.POST.get('respond-vacancy-desired-income'),
                candidate_email=request.POST.get('respond-vacancy-email'),
                candidate_tel=request.POST.get('respond-vacancy-tel'),
                candidate_information=request.POST.get('respond-vacancy-information'),
                candidate_resume=resume_file,
                personal_data_consent=personal_data_consent,
                privacy_policy_acknowledged=privacy_policy_acknowledged,
                consent_recorded_at=timezone.now(),
                privacy_policy_version=PRIVACY_POLICY_VERSION,
            )
            
            # Отправка email уведомления HR о новом отклике
            try:
                job_vacancy = Vacancies.objects.get(id=request.POST.get('vacancies-id'))
                email_sender = SendEmail()
                email_result = email_sender.sendJobApplication(new_candidate, job_vacancy)
                
                if not email_result['success']:
                    print(f"Ошибка отправки email: {email_result['message']}")
            except Exception as email_err:
                print(f"Ошибка при отправке email уведомления: {str(email_err)}")
            
            return JsonResponse({'success': True,
                                 'data': {
                                                'candidate_name': new_candidate.candidate_name,
                                                'email': new_candidate.candidate_email,
                                                'tel': new_candidate.candidate_tel
                                        }
                                 })
        except Exception as err:
            return JsonResponse({'success': False, 'error': str(err)})
    else:
        return JsonResponse({'success': False, 'error':'Только POST запросы'}, status=405)
            

# Страница "Контакты"
def contacts(request):
    form = ProjectForm()
    contact = ContactPage.objects.last()
    representatives = Representatives.objects.all()
    geo_content = list(
        GeographicalPresence.objects.filter(visible_on_map=True).prefetch_related(
            Prefetch(
                'adresses',
                queryset=RegionAdress.objects.filter(visible_on_site=True).order_by('id'),
                to_attr='visible_addresses'
            ),
            'linked_regions'
        ).order_by('region_name')
    )
    geo_map_config = {
        'regionLinks': {
            region.region_code: sorted({
                linked_region.region_code
                for linked_region in region.linked_regions.all()
                if linked_region.region_code
            })
            for region in geo_content
        },
        'cityMarkers': [
            {
                'code': region.region_code,
                'label': region.city_name.strip(),
                'x': region.city_x,
                'y': region.city_y,
                'offsetX': region.city_offset_x,
                'offsetY': region.city_offset_y
            }
            for region in geo_content
            if region.show_city_label and region.city_name.strip()
        ],
        'titlesByCode': {
            region.region_code: region.region_name
            for region in geo_content
        }
    }
    data = {
        'contact': contact,
        'form':form,
        'success_send_form': False,
        'error': '',
        'representatives': representatives,
        'geo_content' : geo_content,
        'geo_map_config': geo_map_config,
        'seo': build_seo(
            'Контакты и представительства компании «Альтернатива»',
            'Контакты завода и региональных представительств «Альтернатива»: '
            'телефоны, адреса и форма отправки проекта.',
        ),
    }
    if request.method == 'GET':
        return render(request, 'contacts.html', data)
    elif request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            clean_form = form.cleaned_data
            if clean_form['consent_personal_data']:
                new_project = Project.objects.create(
                    consumer_name=clean_form['consumer_name'],
                    consumer_email=clean_form['consumer_email'],
                    consumer_tel=clean_form['consumer_tel'],
                    consumer_message=clean_form['consumer_message'],
                    personal_data_consent=clean_form['consent_personal_data'],
                    privacy_policy_acknowledged=clean_form['privacy_policy_acknowledged'],
                    consent_recorded_at=timezone.now(),
                    privacy_policy_version=PRIVACY_POLICY_VERSION,
                )
                
                # Отправка email уведомления менеджеру о новом запросе на проект
                try:
                    email_sender = SendEmail()
                    email_result = email_sender.sendProjectApplication(new_project)
                    
                    if not email_result['success']:
                        print(f"Ошибка отправки email: {email_result['message']}")
                except Exception as email_err:
                    print(f"Ошибка при отправке email уведомления: {str(email_err)}")
                
                data['success_send_form'] = True
            else:
                data['form'] = ProjectForm(request.POST)
                data['error'] = 'Необходимо согласиться на передачу и обработку персональных данных'
                return render(request, 'contacts.html', data)
            return render(request, 'contacts.html', data)
        else:
            return render(request, 'contacts.html', data)

# Страница "Награды"
def rewards(request):
    rewards = Rewards.objects.filter(isActive=True)
    data = {
        'title': 'Награды',
        'rewards': rewards,
        'seo': build_seo(
            'Награды компании «Альтернатива»',
            'Награды и достижения производителя фасадных систем «Альтернатива».',
        ),
    }
    return render(request, 'rewards.html', data)

# Страница "Статьи"
def articles(request, slug_name=None):
    
    articles = Articles.objects.all()[0:10]
    data = {
        'title': 'Статьи',
        'articles': articles,
        'seo': build_seo(
            'Статьи о вентилируемых фасадах — «Альтернатива»',
            'Материалы о проектировании, производстве и применении '
            'навесных вентилируемых фасадных систем.',
        ),
    }
    
    if slug_name is not None:
        article = get_object_or_404(Articles, slug=slug_name)
        data['active_slug'] = slug_name
        data['article_active'] = article
        data['seo'] = build_seo(
            f'{article.article_title} — «Альтернатива»',
            article.article_text,
            page_type='article',
        )
        
    return render(request, 'articles.html', data)

# Страница "Новости"
def news(request, slug_name=None):
    news = News.objects.all().order_by("-id")[0:15]
    data = {
        'title': 'Новости',
        'news': news,
        'seo': build_seo(
            'Новости компании «Альтернатива»',
            'Новости производства, компании и проектов завода фасадных систем «Альтернатива».',
        ),
    }
    if slug_name is not None:
        news_item = get_object_or_404(News, slug=slug_name)
        data['active_slug'] = slug_name
        data['news_active'] = news_item
        data['seo'] = build_seo(
            f'{news_item.news_title} — «Альтернатива»',
            news_item.prev_text or news_item.news_text,
            news_item.get_homepage_image_url(),
            page_type='article',
        )
        
    return render(request, 'news.html', data)

# Страница "Партнеры" (заимствована с сертификатов)
def sertificates(request):
    sertificates_lib = Sertificate.objects.filter(isActive=True)
    data = {
        'title': 'Наши партнеры',
        'sertificates': sertificates_lib,
        'seo': build_seo(
            'Партнеры компании «Альтернатива»',
            'Партнеры производителя фасадных систем «Альтернатива».',
        ),
    }
    
    return render(request, 'sertificates.html', data)

# Страница "Технические свидетельства"
def documents(request):
    doc_lib = Documents.objects.filter(isActive=True)
    data = {
        'title': 'Технические свидетельства',
        'documents': doc_lib,
        'seo': build_seo(
            'Документы и технические свидетельства — «Альтернатива»',
            'Технические свидетельства и разрешительная документация '
            'на фасадные системы «Альт-Фасад».',
        ),
    }
    
    return render(request, 'documents.html', data)

def facadeSystem(request, slug_facade_type=None, slug_facade_name=None):
    menu_items = FacadeSystemBase.objects.all()
    data = {
        'menu_items': menu_items,
        'seo': build_seo(
            'Фасадные системы «Альт-Фасад» — производство и проектирование',
            'Стальные и алюминиевые навесные вентилируемые фасадные системы '
            'для различных облицовочных материалов.',
        ),
    }
    if slug_facade_type == None:
        baseContent = FacadeSystemStartPage.objects.last()
        data['page_content'] = baseContent
        data['page_heading'] = 'Фасадные системы «Альт-Фасад»'
        
    if slug_facade_type is not None and slug_facade_name is None:
        facade_type = get_object_or_404(FacadeSystemBase, facade_base_slug=slug_facade_type)
        data['page_content'] = facade_type
        data['page_heading'] = facade_type.facade_name
        data['active_slug'] = slug_facade_type
        data['bread_crumbs'] = {facade_type.facade_name: f'/facade-system/{facade_type.facade_base_slug}'}
        data['seo'] = build_seo(
            f'{facade_type.facade_name} — системы «Альт-Фасад»',
            facade_type.facade_description,
        )
    
    if slug_facade_type is not None and slug_facade_name is not None:
        facade = get_object_or_404(
            FacadeSystem.objects.select_related('fs_type'),
            fs_type__facade_base_slug=slug_facade_type,
            fs_slug=slug_facade_name,
        )
        data['page_content'] = facade
        data['page_heading'] = facade.fs_name
        data['active_slug'] = slug_facade_name
        data['bread_crumbs'] = {facade.fs_type.facade_name: f'/facade-system/{facade.fs_type.facade_base_slug}', facade.fs_name: f'/facade-system/{facade.fs_type.facade_base_slug}/{facade.fs_slug}'}
        data['seo'] = build_seo(
            f'{facade.fs_name}: {facade.fs_subtext} — «Альтернатива»',
            facade.prev_text or facade.fs_description,
            facade.get_homepage_image_url(),
        )
    
    return render(request, 'facade-system.html', data)


def legacy_facade_redirect(request, legacy_type, legacy_slug):
    slug_aliases = {
        'alt-fasad-c': 'alt-fasad-s',
    }
    facade = get_object_or_404(
        FacadeSystem.objects.select_related('fs_type'),
        fs_slug=slug_aliases.get(legacy_slug, legacy_slug),
    )
    return redirect(
        'facadeSystem-detail',
        slug_facade_type=facade.fs_type.facade_base_slug,
        slug_facade_name=facade.fs_slug,
        permanent=True,
    )
