from django.contrib import admin
from mainSite.models import *

from django_summernote.admin import SummernoteModelAdmin

SUMMERNOTE_FONT_SIZES = [
    '8', '10', '12', '14', '16', '18', '20', '24',
    '28', '32', '36', '40', '48', '56', '64', '72',
]


class ProjectSummernoteModelAdmin(SummernoteModelAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        uses_summernote = (
            self.summernote_fields == '__all__'
            or db_field.name in self.summernote_fields
        )
        if formfield and uses_summernote:
            summernote_options = formfield.widget.attrs.setdefault('summernote', {})
            summernote_options.update({
                'fontSizes': SUMMERNOTE_FONT_SIZES,
                'fontSizeUnits': ['px'],
            })
        return formfield


class AboutUsAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('text_content',)

class TechnologyContentAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('text_content',)

class ArticlesContentAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('article_text',) 
    prepopulated_fields = {'slug': ('article_title',)}

class NewsContentAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('news_text',) 
    prepopulated_fields = {'slug': ('news_title',)}
    readonly_fields = ('prev_text', )
    
class FacadeSystemBaseAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('facade_description',) 
    prepopulated_fields = {'facade_base_slug': ('facade_name',)}

class FacadeSystemAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('fs_description',) 
    prepopulated_fields = {'fs_slug': ('fs_name',)}
    
class FacadeSystemContentPageAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('fs_page_content',) 

class RegionAdressInLine(admin.StackedInline):
    model = RegionAdress
    extra = 0
    verbose_name_plural = "Адреса представительств"

class PortfolioInLine(admin.StackedInline):
    model = PortfolioImage
    can_delete = False
    verbose_name_plural = "Изображения"


class CladdingSystemInLine(admin.StackedInline):
    model = claddingSystemPortfolio
    can_delete = False
    verbose_name_plural = "Облицовки"

class PortfolioInlineImage(admin.ModelAdmin):
    inlines = [PortfolioInLine, CladdingSystemInLine]
    prepopulated_fields = {'slug': ('title',)}  # указываем, что slug генерируется из title
    search_fields = ['title',]
    filter_horizontal = ('facade_systems',)



class RegionInLine(admin.ModelAdmin):
    inlines = [RegionAdressInLine]
    list_display = ('region_name', 'region_code', 'visible_on_map', 'show_city_label', 'city_name', 'city_x', 'city_y', 'city_offset_x', 'city_offset_y')
    list_filter = ('visible_on_map', 'show_city_label')
    search_fields = ['region_name', 'region_code', 'city_name']
    filter_horizontal = ('linked_regions',)
    fieldsets = (
        ('Регион', {
            'fields': ('region_name', 'region_code', 'visible_on_map')
        }),
        ('Подсветка', {
            'fields': ('linked_regions',)
        }),
        ('Popup', {
            'fields': ('popup_description',)
        }),
        ('Город на карте', {
            'fields': ('show_city_label', 'city_name', 'city_x', 'city_y', 'city_offset_x', 'city_offset_y')
        }),
    )
    
    
class ProductModelAdmin(ProjectSummernoteModelAdmin):
    summernote_fields = ('product_description',)
    list_display = ('product_name', 'product_type', 'sort_order')
    list_editable = ('sort_order',)
    list_filter = ('product_type',)
    search_fields = ('product_name',)


class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'product_link', 'sort_order')
    list_editable = ('sort_order',)
    ordering = ('sort_order', 'product_type')


class VacanciesAdmin(admin.ModelAdmin):
    exclude = ('requirements',)
    list_display = ('title', 'region', 'salary', 'isActive', 'last_update')
    list_filter = ('isActive', 'region')


class VacanciesApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'job', 'personal_data_consent', 'privacy_policy_acknowledged', 'consent_recorded_at')
    list_filter = ('personal_data_consent', 'privacy_policy_acknowledged')
    readonly_fields = (
        'personal_data_consent',
        'privacy_policy_acknowledged',
        'consent_recorded_at',
        'privacy_policy_version',
    )


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('consumer_name', 'consumer_email', 'personal_data_consent', 'privacy_policy_acknowledged', 'consent_recorded_at')
    list_filter = ('personal_data_consent', 'privacy_policy_acknowledged')
    readonly_fields = (
        'personal_data_consent',
        'privacy_policy_acknowledged',
        'consent_recorded_at',
        'privacy_policy_version',
    )
    
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
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductModelAdmin)
admin.site.register(Portfolio, PortfolioInlineImage)
admin.site.register(TechnologyPageContent, TechnologyContentAdmin)
admin.site.register(VacanciesPageContent)
admin.site.register(Vacancies, VacanciesAdmin)
admin.site.register(VacanciesApplication, VacanciesApplicationAdmin)
admin.site.register(ContactPage)
admin.site.register(Project, ProjectAdmin)
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
