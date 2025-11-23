from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .sendMail import SendEmail
import json
from .forms import ProjectForm


# Представление страниц
# Главная страница
def index(request):
    uuid = 'index'
    title_content = PageContent.objects.get(page_uuid=uuid)
    geo_content = RegionAdress.objects.filter(visible_on_site=True)
    product_content = ProductionBase.objects.all()
    portfolio_lib = Portfolio.objects.all()
    news_lib = News.objects.all().order_by('created_at')[0:10]
    fs_system = FacadeSystem.objects.filter(display_in_main=True)
    data = {
        'title_content' : title_content,
        'geo_content' : geo_content,
        'product_content' : product_content,
        'portfolio_lib': portfolio_lib,
        'news_lib': news_lib,
        'fs_system': fs_system
    }
    
    return render(request,'main.html', data)

def products(request, prod_type = 'all'):
    
    if prod_type == 'all':
        products_library = Product.objects.all()
        bread_crumbs = {
            '/': 'Главная',
            '/production/': 'Продукция',
        }
    elif prod_type == 'klyamer':
        products_library = Product.objects.filter(product_type_id=1)
        bread_crumbs = {
            '/': 'Главная',
            '/production/': 'Продукция',
            '/production/klyamer/':'Кляммеры'
        }
    elif prod_type == 'facade-brackets':
        products_library = Product.objects.filter(product_type_id=2)
        bread_crumbs = {
            '/': 'Главная',
            '/production/': 'Продукция',
            '/production/facade-brackets/':'Фасадные кронштейны'
        }
    elif prod_type == 'facade-profile':
        products_library = Product.objects.filter(product_type_id=3)
        bread_crumbs = {
            '/': 'Главная',
            '/production/': 'Продукция',
            '/production/facade-profile/':'Фасадные профили'
        }
    else:
        raise Http404 
    
    data = {
        'products': products_library,
        'bread_crumbs': bread_crumbs
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
        'bread_crumbs': bread_crumbs
        }
    return render(request, 'about.html', data)

# Страница "Портфолио"
def portfolio(request, slug_name=None):
    if request.method == 'GET':
        portfolio_lib = Portfolio.objects.all()
        data = {
            'portfolio_lib': portfolio_lib
        }
        return render(request, 'portfolio.html', data)
    elif request.method == 'POST':
        try:
        # Получаем JSON-данные из тела запроса
            received_data = json.loads(request.body)
            portfolio_id = received_data['portfolio_id']
            # Обрабатываем данные
            images_list = Portfolio.objects.get(id=portfolio_id).getAllImages()
            images = []
            for image in images_list:
                images.append({
                    'id': image.id,
                    'src': image.image_link.url,
                    'caption': image.alt
                })
            
            
            processed_data = {
                'success': True,
                'data': images
            }
            
            return JsonResponse(processed_data, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
            
    else:
        raise Http404 
    

# Страница "Технологии"
def technology(request):
    content = TechnologyPageContent.objects.last()
    data = {
        'title': 'Технологии',
        'content': content
    }
    return render(request, 'services.html', data)

# Страница "Вакансии"
def job(request, job_id=None):
    if request.method == 'GET':
        content = VacanciesPageContent.objects.all()
        vacancies = Vacancies.objects.filter(isActive=True).order_by('created_at')
        data = {
            'content': content,
            'vacancies': vacancies
        }
        return render(request, 'job.html', data)
    elif request.method == 'POST':
        job = Vacancies.objects.get(id=job_id)
        job_content = {
            'id': job.id,
            'title': job.title,
            'region': job.region,
            'requirements': job.requirements,
            'responsibilities': job.responsibilities
        }
        if job:
            return JsonResponse({'success': True, 'data': job_content})
        else:
            return JsonResponse({'success': False, 'error': 'Запись не найдена'})
    else:
        return JsonResponse({'success': False, 'error': 'Недопустимый метод'}, status=500)

# Отклик на вакансию

def jobApplication(request):
    if request.method == 'POST':
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
                candidate_resume=resume_file
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
        return JsonResponse({'success': False, 'error':'Только POST запросы'}, status=500)
            

# Страница "Контакты"
def contacts(request):
    form = ProjectForm()
    contact = ContactPage.objects.last()
    data = {
        'contact': contact,
        'form':form,
        'success_send_form': False,
        'error': ''
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
        'rewards': rewards
    }
    return render(request, 'rewards.html', data)

# Страница "Статьи"
def articles(request, slug_name=None):
    
    articles = Articles.objects.all()[0:10]
    data = {
        'title': 'Статьи',
        'articles': articles
    }
    
    if slug_name != None:
        article = Articles.objects.filter(slug=slug_name)
        data['active_slug'] = slug_name
        data['article_active'] = article
        
    return render(request, 'articles.html', data)

# Страница "Новости"
def news(request, slug_name=None):
    news = News.objects.all()[0:10]
    data = {
        'title': 'Новости',
        'news': news
    }
    if slug_name != None:
        news_item = News.objects.filter(slug=slug_name)
        data['active_slug'] = slug_name
        data['news_active'] = news_item
        
    return render(request, 'news.html', data)

# Страница "Сертификаты"
def sertificates(request):
    sertificates_lib = Sertificate.objects.filter(isActive=True)
    data = {
        'title': 'Сертификаты',
        'sertificates': sertificates_lib
    }
    
    return render(request, 'sertificates.html', data)

# Страница "Технические свидетельства"
def documents(request):
    doc_lib = Documents.objects.filter(isActive=True)
    data = {
        'title': 'Технические свидетельства',
        'documents': doc_lib
    }
    
    return render(request, 'documents.html', data)

def facadeSystem(request, slug_facade_type=None, slug_facade_name=None):
    menu_items = FacadeSystemBase.objects.all()
    data = {
        'menu_items': menu_items
    }
    if slug_facade_type == None:
        baseContent = FacadeSystemStartPage.objects.last()
        data['page_content'] = baseContent
        
    if slug_facade_type != None and slug_facade_name == None:
        facade_type = FacadeSystemBase.objects.filter(facade_base_slug=slug_facade_type)[0]
        data['page_content'] = facade_type
        data['active_slug'] = slug_facade_type
        data['bread_crumbs'] = {facade_type.facade_name: f'/facade-system/{facade_type.facade_base_slug}'}
    
    if slug_facade_type != None and slug_facade_name != None:
        facade = FacadeSystem.objects.filter(fs_slug=slug_facade_name)[0]
        data['page_content'] = facade
        data['active_slug'] = slug_facade_name
        data['bread_crumbs'] = {facade.fs_type.facade_name: f'/facade-system/{facade.fs_type.facade_base_slug}', facade.fs_name: f'/facade-system/{facade.fs_type.facade_base_slug}/{facade.fs_slug}'}
    
    return render(request, 'facade-system.html', data)