from django.contrib import admin
from mainSite.models import *

from django_summernote.admin import SummernoteModelAdmin

class AboutUsAdmin (SummernoteModelAdmin):
    summernote_fields = ('text_content',)

class TechnologyContentAdmin(SummernoteModelAdmin):
    summernote_fields = ('text_content',)

class ArticlesContentAdmin(SummernoteModelAdmin):
    summernote_fields = ('article_text',) 
    prepopulated_fields = {'slug': ('article_title',)}

class NewsContentAdmin(SummernoteModelAdmin):
    summernote_fields = ('news_text',) 
    prepopulated_fields = {'slug': ('news_title',)}
    readonly_fields = ('prev_text', )
    
class FacadeSystemBaseAdmin(SummernoteModelAdmin):
    summernote_fields = ('facade_description',) 
    prepopulated_fields = {'facade_base_slug': ('facade_name',)}

class FacadeSystemAdmin(SummernoteModelAdmin):
    summernote_fields = ('fs_description',) 
    prepopulated_fields = {'fs_slug': ('fs_name',)}
    
class FacadeSystemContentPageAdmin(SummernoteModelAdmin):
    summernote_fields = ('fs_page_content',) 

class PortfolioInLine(admin.StackedInline):
    model = PortfolioImage
    can_delete = False
    verbose_name_plural = "Изображения"

class RegionAdressInLine(admin.StackedInline):
    model = RegionAdress
    can_delete = False
    verbose_name_plural = "Адреса представительств"

class PortfolioInlineImage(admin.ModelAdmin):
    inlines = [PortfolioInLine]
    prepopulated_fields = {'slug': ('title',)}  # указываем, что slug генерируется из title
    search_fields = ['title',]

class RegionInLine(admin.ModelAdmin):
    inlines = [RegionAdressInLine]
    search_fields = ['region_name',]
    
    
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_type') 
    list_filter = ('product_type',)
    
class RepresentativesAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'company_name') 
    list_filter = ('country', 'city')
    search_fields = ['city', 'company_name']


# Register your models here.
admin.site.register(ProductionBase)
admin.site.register(ProductPart)
admin.site.register(PageContent)
admin.site.register(GeographicalPresence, RegionInLine)
admin.site.register(AboutUs, AboutUsAdmin)
admin.site.register(ProductType)
admin.site.register(Product, ProductModelAdmin)
admin.site.register(Portfolio, PortfolioInlineImage)
admin.site.register(TechnologyPageContent, TechnologyContentAdmin)
admin.site.register(VacanciesPageContent)
admin.site.register(Vacancies)
admin.site.register(VacanciesApplication)
admin.site.register(ContactPage)
admin.site.register(Project)
admin.site.register(Rewards)
admin.site.register(Articles, ArticlesContentAdmin)
admin.site.register(News, NewsContentAdmin)
admin.site.register(Sertificate)
admin.site.register(Documents)
admin.site.register(FacadeSystemBase, FacadeSystemBaseAdmin)
admin.site.register(FacadeSystem, FacadeSystemAdmin)
admin.site.register(FacadeSystemStartPage, FacadeSystemContentPageAdmin)
admin.site.register(RepresentativesCountry)
admin.site.register(Representatives, RepresentativesAdmin)