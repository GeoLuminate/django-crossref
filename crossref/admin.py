from django.contrib import admin
from django.utils.html import mark_safe
from django.urls import path
from .forms import CrossRefForm, DOIForm, UploadForm, WorkAdminForm, BibtexForm
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template.defaultfilters import pluralize
from requests.exceptions import HTTPError
from django.db.models import Count
from .models import Work, Author, Funder, Settings
from solo.admin import SingletonModelAdmin
from django.contrib import messages
from django.utils.html import mark_safe
from io import TextIOWrapper
import bibtexparser as bib
from tqdm import tqdm
from crossref.parsers import bibtex

class ChangeListQuickAdd():
    select2 = {}
    change_list_template = 'admin/crossref/quick_add.html'
    
    def changelist_view(self, request, extra_context={}):
        extra_context['select2'] = self.select2
        extra_context['select'] = self.get_model_fields()
        extra_context['doi_form'] = DOIForm()
        extra_context['bibtex_import_form'] = UploadForm()
        return super().changelist_view(request, extra_context)

    def get_model_fields(self):
        return [f.name.replace('_','-') for f in self.model._meta.get_fields()]


class CrossRefMixin(ChangeListQuickAdd, admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                # 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',
                'crossref/select2/select2.css',
                )
        }
        js = (
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
            'crossref/js/crossref.js',
        )


class WorkAdminMixin(CrossRefMixin):
    change_list_template = 'admin/crossref/grappelli_quick_doi.html'
    form = WorkAdminForm 
    
    select2 = {
        'endpoint': 'https://api.crossref.org/works',
        'id': 'DOI',
        'text': 'container-title',
        'ajax': {
            'data': {
                ''
            }
        }
    }
    date_hierarchy = 'published'
    raw_id_fields = ('author',)
    autocomplete_lookup_fields = {'m2m': ['author']}
    list_display_links = ('title',)

    list_display = ['article', 'label', 'title', 'container_title', 'is_referenced_by_count', 'published','issue','volume','page','type',]

    list_filter = ['type', 'container_title','language',]
    search_fields = ('DOI', 'title', 'id', 'label')
    
    fieldsets = [
        ('', {'fields':[
            'DOI',
            ('type', 'published'),
            'title',
            'author',
            'container_title',
            'volume',
            'issue',
            'page',
            'abstract',
            ]}),
        ('Additional', {'fields':[
            'language',
            ]}),
        ]

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('author')

    def get_urls(self):
        return [
            path('import-bibtex/', self.admin_site.admin_view(self.import_bibtex), name='import_bibtex'),
            path('add-doi/', self.admin_site.admin_view(self.get_doi_or_query_crossref), name='add_from_crossref'),
        ] + super().get_urls()

    def get_doi_or_query_crossref(self, request, *args, **kwargs):
        if request.POST:
            form = DOIForm(request.POST)
            if form.is_valid():
                self._get_data_from_crossref(request, form.cleaned_data['DOI'])
            else:
                if form.errors['DOI'][0] == 'Work with this DOI already exists.':
                    message = f"An item with that DOI already exists in the database: {form.data['DOI']}"
                else:
                    message = mark_safe("<br>".join(e for e in form.errors['DOI']))
                self.message_user(request, message, messages.INFO) 
        return HttpResponseRedirect('../')
     
    def _get_data_from_crossref(self, request, doi):
        try:
            # either retrieve the object from the database, or query crossref for the info
            instance, created = self.get_queryset(request).get_or_query_crossref(doi)
        except HTTPError as e:
            # Something wen't wrong during the request to crossref
            self.message_user(request, e, messages.ERROR)
            return None # return None so the calling function knows something wen't wrong
        
        if created:
            message = mark_safe(f"Succesfully added: {instance.bibliographic()}")
            self.message_user(request, message, messages.SUCCESS)
        else:
            message = f"{instance.DOI} already exists in this database"
            self.message_user(request, message, messages.INFO)

        return instance
        
    def import_bibtex(self, request, *args, **kwargs):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            with TextIOWrapper(form.cleaned_data['file'].file, encoding='utf-8') as f:
                bib = bibtex.parse(f.read())
                
            
            pbar = tqdm(total=len(bib))
            for entry in bib:   
                
                if entry.get('doi'):
                    # If the bibtex entry has a DOI, use it to fetch data from crossref
                    if self._get_data_from_crossref(request, entry.get('doi')):
                        continue

                bibtex_form = BibtexForm(entry)
                if bibtex_form.is_valid():
                    bibtex_form.save()
                else:
                    # probably append to some error list and return later
                    pass

                pbar.update(1)


            # messages.info(request, f"Added {len(publications)} publication{pluralize(publications, ',s')}.")
            
        return HttpResponseRedirect('../')

    def article(self, obj):
        if obj.DOI:
            return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(obj.DOI))
        else:
            return ''
        
    def file(self, obj):
        if obj.pdf:
            return mark_safe(f'<a href="{obj.pdf.url}"><i class="fas fa-file-pdf fa-2x"></i></a>')
        else:
            return ""




class AuthorAdminMixin(CrossRefMixin):

    list_display = ['prefix','given', 'family','suffix','ORCID','authenticated_orcid','_works']
    search_fields = ['family', 'given', 'ORCID']
    list_filter = ['authenticated_orcid',]

    def get_queryset(self, request):
        return (
        super().get_queryset(request)
        .prefetch_related('works')
        .annotate(_works=Count('works')))

    def _works(self, object):
        return object._works
    _works.admin_order_field = '_works'
    _works.short_description  = _('Works')


class FunderAdminMixin(CrossRefMixin):
    select2 = {
        'endpoint': 'https://api.crossref.org/funders',
        'id': 'id',
        'text': 'name'
    }

    list_display = ['id', 'name', 'location','uri']
    search_fields = ['name', 'id',]
    list_filter = ['location',]

admin.site.register(Settings, SingletonModelAdmin)
admin.site.register(Work, WorkAdminMixin)
admin.site.register(Author, AuthorAdminMixin)
admin.site.register(Funder, FunderAdminMixin)