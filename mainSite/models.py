from django.db import models
from django.utils.text import slugify
from django.utils.html import strip_tags


class ProductionBase(models.Model):
    title = models.CharField(max_length=100)
    inner_path = models.BooleanField()
    path = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title
    
class ProductPart(models.Model):
    part_name = models.CharField(max_length=150)
    part_text = models.CharField(max_length=350, blank=True)
    product_base = models.ForeignKey(ProductionBase, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.part_name
    
    
class PageContent(models.Model):
    page_uuid = models.CharField(max_length=150, blank=False)
    title = models.CharField(max_length=100, blank=False)
    sub_title = models.CharField(max_length=350, blank=False)
    production = models.ManyToManyField(ProductionBase)
    
    def __str__(self):
        return self.page_uuid

class GeographicalPresence(models.Model):
    region_name = models.CharField(max_length=150, blank=False, verbose_name = 'Наименование региона')
    region_code = models.CharField(max_length=50, blank=False, verbose_name = 'КОД')
    
    class Meta:
        verbose_name = 'Регион и представительства'
        verbose_name_plural = 'Регионы и представительства' 
    
    def __str__(self):
        return self.region_name
    
class RegionAdress(models.Model):
    adress_name = models.TextField(verbose_name = 'Адрес')
    geographical_presence = models.ForeignKey(GeographicalPresence, related_name='adresses', on_delete=models.CASCADE)
    visible_on_site = models.BooleanField(default=False, verbose_name = 'Включить на сайте?')
    
    class Meta:
        verbose_name = 'Адрес представительства'
        verbose_name_plural = 'Адреса представительства' 
    
    def __str__(self):
        return self.adress_name
    
class AboutUs(models.Model):
    text_content = models.TextField()
    last_update = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Страница "О нас"'
        verbose_name_plural = 'Страница "О нас"' 
    
    def __str__(self):
        return 'Контент от ' + str(self.last_update)

class ProductType(models.Model):
    product_type = models.CharField(max_length=150, blank=False, verbose_name = 'Тип продукта')
    
    class Meta:
        verbose_name = 'Тип продукта (Админ)'
        verbose_name_plural = 'Типы продуктов (Админ)'
    
    def __str__ (self):
        return self.product_type
    
class Product(models.Model):
    product_name = models.CharField(max_length=350, blank=False, verbose_name = 'Наименование продукта')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name = 'Тип продукта')
    product_img = models.FileField(upload_to=f'production/', blank=True, verbose_name = 'Изображение')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
    
    def __str__ (self):
        return self.product_name


class Portfolio(models.Model):
    title = models.CharField(max_length=350, blank=False, verbose_name = 'Наименование портфолио')
    main_img = models.FileField(upload_to='portfolio/', blank=False, verbose_name = 'Главное изображение')
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='URL-ссылка'
    )
    
    class Meta:
        verbose_name = 'Портфолио'
        verbose_name_plural = 'Портфолио' 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def getAllImages(self):
        return self.images.all()
        
    def __str__(self):
        return self.title

class PortfolioImage(models.Model):
    alt = models.CharField(max_length=150, blank=False, verbose_name = 'Описание к изображению')
    image_link = models.FileField(upload_to='portfolio/', blank=False, verbose_name = 'Изображение')
    portfolio = models.ForeignKey(
        Portfolio,
        related_name='images',
        on_delete = models.CASCADE
    )
    
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
    
    def __str__(self):
        return self.alt
    
class TechnologyPageContent(models.Model):
    text_content = models.TextField()
    last_update = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Страница "Технолногии"'
        verbose_name_plural = 'Страница "Технологии"' 
    
    def __str__(self):
        return 'Контент от ' + str(self.last_update)
    
class VacanciesPageContent(models.Model):
    priority_title = models.CharField(max_length=50, blank=False, verbose_name='Заголовок')
    priority_text = models.CharField(max_length=100, blank=False, verbose_name='Дополнительное описание')
    priority_img = models.FileField(upload_to='vacancies_page_content/', blank=False, verbose_name = 'картинка (только в формате svg)')
    class_name = models.CharField(max_length=150, blank=True, verbose_name='Класс для страницы', help_text='Не менять', default='None')
    last_update = models.DateTimeField()
    
    class Meta:
        verbose_name='Страница "Вакансии"'
        verbose_name_plural = 'Страница "Вакансии"'
    
    def __str__(self):
        return self.priority_title
    
class Vacancies(models.Model):
    title = models.CharField(max_length=75, blank=False, verbose_name='Наименование вакансии')
    region = models.CharField(max_length=75, blank=True, verbose_name='Город для работы', default='Трехгорный', help_text='Если не указать, атвтоматически будет установлено "Трехгорный"')
    work_schedule = models.CharField(max_length=15, blank=False, verbose_name='График работы', default='5/2')
    salary = models.IntegerField(verbose_name='Размер оплаты труда', blank=True)
    requirements = models.TextField(verbose_name='Требования', help_text='Требования необходимо указывать через запятую', blank=True)
    responsibilities = models.TextField(verbose_name='Обязанности', help_text='Обязанности необходимо указывать через запятую', blank=True)
    isActive = models.BooleanField(verbose_name='Активная вакансия?')
    created_at = models.DateTimeField(verbose_name='Заявка создана', auto_now_add=True, blank=True)
    last_update = models.DateTimeField(verbose_name='Последнее обновление')
    
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
    
    def __str__(self):
        return self.title

class VacanciesApplication(models.Model):
    job = models.ForeignKey(
       Vacancies,
       related_name='job_applications',
       on_delete = models.CASCADE 
    )
    candidate_name = models.CharField(max_length=100, blank=False, verbose_name='ФИО кандидата')
    candidate_birthday = models.TextField(blank=True, verbose_name='Дата и место рождения', default='Не указаны')
    candidate_adress = models.CharField(max_length=200, blank=True, verbose_name='Место жительства', default='Не указан')
    candidate_education_level = models.CharField(max_length=150, blank=False, verbose_name='Уровень образования кандидата')
    candidate_subeducation_level = models.TextField(blank=True, verbose_name='Дополнительное образование кандидата', default='Не указано')
    candidate_marital_status = models.CharField(max_length=50, blank=False, verbose_name='Семейное положение')
    candidate_desire_income = models.IntegerField(blank=True, verbose_name='Уровень желаемого дохода', default=0)
    candidate_email = models.CharField(max_length=100, blank=False, verbose_name='Email кандидата')
    candidate_tel = models.CharField(max_length=20, blank=False, verbose_name='Телефон кандидата')
    candidate_information = models.TextField(blank=True, verbose_name='Дополнительная информация о кандидате', default='Не указано дополнительных сведений')
    candidate_resume = models.FileField(upload_to='candidate_resume/', blank=True, verbose_name='Резюме кандидата')
    
    class Meta:
        verbose_name = 'Отклик на вакансию'
        verbose_name_plural = 'Отклики на вакансии'
        
    def __str__(self):
        return self.candidate_name

class ContactPage(models.Model):
    org_name = models.CharField(max_length=100, blank=False, verbose_name='Наименование организации')
    org_adress = models.CharField(max_length=150, blank=False, verbose_name='Адрес организации')
    org_phone = models.CharField(max_length=150, blank=False, verbose_name='Телефон организации')
    org_fax = models.CharField(max_length=150, blank=False, verbose_name='Факс организации')
    org_email = models.CharField(max_length=150, blank=False, verbose_name='Email организации')
    
    class Meta:
        verbose_name = 'Контакт организации'
        verbose_name_plural = 'Контакты организации'
        
    def __str__(self):
        return self.org_name

class Project(models.Model):
    consumer_name = models.CharField(max_length=100, blank=False, verbose_name='Имя отправителя')
    consumer_email = models.CharField(max_length=100, blank=False, verbose_name='Email отправителя')
    consumer_tel = models.CharField(max_length=100, blank=False, verbose_name='Телефон отправителя')
    consumer_message = models.TextField(blank=True, verbose_name='Сообщение', default='Нет описания')
    
    class Meta:
        verbose_name = 'Обращение с проектом'
        verbose_name_plural = 'Обращения с проектами'
        
    def __str__(self):
        return self.consumer_name
    
class Rewards(models.Model):
    reward_title = models.CharField(max_length=100, blank=False, verbose_name='Заголовок изображения')
    reward_img = models.FileField(upload_to='rewards/', blank=False, verbose_name='Изображение награды')
    reward_description = models.TextField(blank=False, verbose_name='Краткое описание', default='Нет описания')
    isActive = models.BooleanField(verbose_name='Активная награда?', default=True)
    
    class Meta:
        verbose_name = 'Награда'
        verbose_name_plural = 'Награды'
        
    def __str__(self):
        return self.reward_title

class Articles(models.Model):
    article_title = models.CharField(max_length=350, blank=False, verbose_name = 'Заголовок статьи')
    article_text = models.TextField(blank=False, verbose_name='Текст статьи')
    created_at = models.DateTimeField(verbose_name='Статья создана', auto_now_add=True, blank=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='URL-ссылка'
    )
    
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи' 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.article_title)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.article_title

class News(models.Model):
    news_title = models.CharField(max_length=350, blank=False, verbose_name = 'Заголовок новости')
    title_img = models.FileField(upload_to='news/title-img/', blank=False, verbose_name='Главное изображение новости')
    news_text = models.TextField(blank=False, verbose_name='Текст новости')
    prev_text = models.CharField(max_length=150, blank=True, verbose_name = 'Превью новости')
    created_at = models.DateTimeField(verbose_name='Новость создана', auto_now_add=True, blank=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='URL-ссылка'
    )
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости' 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.news_title)
        # Strip HTML tags from news_text and create preview
        clean_text = strip_tags(self.news_text).strip()
        if clean_text:
            self.prev_text = clean_text[:130] + '...' if len(clean_text) > 130 else clean_text
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.news_title

class Sertificate(models.Model):
    sert_title = models.CharField(max_length=100, blank=False, verbose_name='Заголовок сертификата')
    sert_description = models.TextField(blank=False, verbose_name='Краткое описание', default='Нет описания')
    sert_img = models.FileField(upload_to='sertificates/', blank=False, verbose_name='Изображение сертификата')
    isActive = models.BooleanField(verbose_name='Активный сертификат?', default=True)
    
    class Meta:
        verbose_name = 'Серитфикат'
        verbose_name_plural = 'Сертификаты'
        
    def __str__(self):
        return self.sert_title

class Documents(models.Model):
    doc_title = models.CharField(max_length=100, blank=False, verbose_name='Название технического свидетельства')
    doc_description = models.TextField(blank=False, verbose_name='Краткое описание', default='Нет описания')
    doc_img = models.FileField(upload_to='documents/', blank=False, verbose_name='Изображение технического свидетельства')
    isActive = models.BooleanField(verbose_name='Активный документ?', default=True)
    
    class Meta:
        verbose_name = 'Техническое свидетельство'
        verbose_name_plural = 'Технические свидетельства'
        
    def __str__(self):
        return self.doc_title

class FacadeSystemBase(models.Model):
    facade_name = models.CharField(max_length=100, blank=False, verbose_name='Наименование типа фасадной системы')
    facade_description = models.TextField(blank=False, verbose_name='Описание системы', default='Нет описания')
    facade_base_slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='URL-ссылка'
    )
    
    class Meta:
        verbose_name = 'Тип фасадной системы'
        verbose_name_plural = 'Типы фасадных систем' 
    
    def save(self, *args, **kwargs):
        if not self.facade_base_slug:
            self.facade_base_slug = slugify(self.facade_name)
        super().save(*args, **kwargs)
        
    def getAllFacadeSystem(self):
        return self.systems.all()
        
    def __str__(self):
        return self.facade_name
    
class FacadeSystem(models.Model):
    fs_name = models.CharField(max_length=100, blank=False, verbose_name='Наименование фасадной системы')
    fs_subtext = models.CharField(max_length=100, blank=False, verbose_name='Подпись для фасадной системы')
    fs_description = models.TextField(blank=False, verbose_name='Описание системы', default='Нет описания')
    fs_type = models.ForeignKey(FacadeSystemBase, verbose_name="Тип системы", on_delete=models.CASCADE, related_name='systems')
    fs_slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='URL-ссылка'
    )
    display_in_main = models.BooleanField(verbose_name='Показать на главной странице?', default=True)
    main_img = models.FileField(upload_to='fasad_img/', blank=False, verbose_name='Заглавное изображение (для главной страницы)')
    prev_text = models.CharField(max_length=150, blank=True, verbose_name = 'Превью описания')
    
    class Meta:
        verbose_name = 'Фасадная система'
        verbose_name_plural = 'Фасадные системы' 
    
    def save(self, *args, **kwargs):
        if not self.fs_slug:
            self.fs_slug = slugify(self.fs_name)
        # Strip HTML tags from news_text and create preview
        clean_text = strip_tags(self.fs_description).strip()
        if clean_text and not self.prev_text:
            self.prev_text = clean_text[:130] + '...' if len(clean_text) > 130 else clean_text
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.fs_name

class FacadeSystemStartPage(models.Model):
    fs_page_content = models.TextField(blank=False, verbose_name='Контент стартовой сраницы', default='Нет описания')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    
    class Meta:
        verbose_name = 'Контент "Фасадные системы"'
        verbose_name_plural = 'Контент "Фасадные системы"' 
        
    def __str__(self):
        return 'Контент от ' + str(self.created_at)
    
class RepresentativesCountry(models.Model):
    full_country_name_rus = models.CharField(max_length=50, blank=True, verbose_name = 'Полное наименование страны на русском')
    full_country_name_eng = models.CharField(max_length=50, blank=True, verbose_name = 'Полное наименование страны на английском')
    short_country_name_rus = models.CharField(max_length=10, blank=True, verbose_name = 'Сокращенное наименование страны на русском')
    short_country_name_eng = models.CharField(max_length=10, blank=True, verbose_name = 'Сокращенное наименование страны на английском')
    
    class Meta:
        verbose_name = 'Страна (справочник)'
        verbose_name_plural = 'Страны (справочник)' 
        
    def __str__(self):
        return self.full_country_name_rus

class Representatives(models.Model):
    country = models.ForeignKey(RepresentativesCountry, verbose_name='Страна', on_delete=models.CASCADE)
    city = models.CharField(max_length=30, blank=False, verbose_name = 'Город')
    company_name = models.CharField(max_length=130, blank=False, verbose_name = 'Наименование организации (полное)')
    company_adress = models.CharField(max_length=50, blank=True, verbose_name = 'Адрес организации')
    company_phone = models.CharField(max_length=50, blank=False, verbose_name = 'Телефон организации')
    company_email = models.CharField(max_length=50, blank=False, verbose_name = 'Email организации')
    
    class Meta:
        verbose_name = 'Представительство'
        verbose_name_plural = 'Представительства' 
        
    def __str__(self):
        return f'{self.city} ({self.country.full_country_name_rus}), компания - {self.company_name}'