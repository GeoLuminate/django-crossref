from django.contrib import admin
from django.utils.html import mark_safe
from django.urls import path
from .forms import CrossRefForm
from django.shortcuts import render
from django.utils.translation import gettext as _
from io import TextIOWrapper
import bibtexparser as bib
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
import pandas as pd
from crossref.forms import UploadForm, PublicationForm
from django.template.defaultfilters import pluralize
from tqdm import tqdm
from django.conf import settings
from habanero import Crossref
from .utils import get_publication_model
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from django_super_deduper.merge import MergedModelInstance
from django.contrib.admin.models import LogEntry, ContentType
from requests.exceptions import HTTPError
from django.db.models import Count, Case, When, IntegerField, Q

Publication = get_publication_model()

class PublicationAdminMixin(admin.ModelAdmin):

    date_hierarchy = 'published'
    raw_id_fields = ('author',)
    autocomplete_lookup_fields = {'m2m': ['author']}
    list_display_links = ('title',)

    list_display = ['file','article', 'label', 'title', 'container_title', 'is_referenced_by_count', 'published','issue','volume','page','type']

    list_filter = ['type', 'source','container_title','language',]
    search_fields = ('DOI', 'title','id','bibtex','label')
    readonly_fields = ['bibtex',]
    fieldsets = [
        (None, {
            'fields':[
                'pdf',
                ]}
            ),
        ('Information', {'fields':[
            'DOI',
            ('type', 'published'),
            'title',
            'author',
            'container_title',
            'volume',
            'issue',
            'page',
            ]}),
        ('Additional', {'fields':[
            'language',
            'source',
            'bibtex',
            ]}),
        ]

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",)

    def get_urls(self):
        return [
            path('import_bibtex/', self.admin_site.admin_view(self.import_bibtex), name='import_bibtex'),
            path('add_from_crossref/', self.admin_site.admin_view(self.add_from_crossref), name='add_from_crossref'),
        ] + super().get_urls()

    def add_from_crossref(self, request, *args, **kwargs):
        context = dict(
           self.admin_site.each_context(request),
           form=CrossRefForm,
        )

        if request.POST:
            form = CrossRefForm(request.POST, request.FILES)
            if form.is_valid():
                dois = [f.strip() for f in form.cleaned_data['DOI'].split(',')]

                saved = []
                for doi in dois:
                    pub_pk = self.save_from_crossref(request, doi)
                    saved.append(pub_pk)

                messages.info(request, f"Added {len(dois)} publication{pluralize(dois, ',s')}.")
                return HttpResponseRedirect('../')

        return render(request, 
            "admin/crossref/import_doi.html", 
            dict(self.admin_site.each_context(request),form=CrossRefForm)
            )

    def import_bibtex(self, request, *args, **kwargs):
        context = dict(
           self.admin_site.each_context(request),
           form=UploadForm,
            )
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = TextIOWrapper(form.cleaned_data['file'].file, encoding='utf-8')
            bibtex = bib.load(f)
            pbar = tqdm(total=len(bibtex.entries))

            # try adding publications
            for label, entry in bibtex.entries_dict.items():
                
                try:
                    instance = Publication.objects.get(label=label)
                except Publication.DoesNotExist:
                    continue

                if entry.get('doi'):
                    # use the DOI to query data from crossref
                    pub_pk = self.save_from_crossref(request, entry.get('doi'), instance)
                    # raise ValueError('No Pub PK')
                    if not pub_pk:
                        self.parse_bibtex(entry, instance)
                else:
                    self.parse_bibtex(entry, instance)
                
                # publications.append(pub_pk)
                pbar.update(1)


            # messages.info(request, f"Added {len(publications)} publication{pluralize(publications, ',s')}.")
            return HttpResponseRedirect('../')

        return render(request, 
            'admin/crossref/import_bibtex.html', 
            dict(self.admin_site.each_context(request),form=UploadForm)
            )

    def bib_entry_to_string(self, entry):
        db = BibDatabase()
        db.entries = [entry]
        return BibTexWriter().write(db)

    def parse_bibtex(self, entry, instance):

        entry['bibtex'] = self.bib_entry_to_string(entry)
        authors = []
        for a in entry.get('author','').split(' and '):
            parts = a.split(' ')
            fields = ['given','family']
            authors.append({k:v for k, v in zip(fields, parts)})

        entry['author'] = authors
        entry['type'] = entry.get('type',entry['ENTRYTYPE'])
        if entry.get('owner'):
            del entry['owner']

        if instance.label:
            entry['label'] = instance.label

        pubform = PublicationForm(entry, instance=instance)
        if pubform.is_valid():
            pubform.save()
            return pubform.instance
        else:
            print('Submission invalid')
            print(pubform.errors)

    def save_from_crossref(self, request, doi, instance=None, update=True):

        qs = self.get_queryset(request).filter(DOI=doi)
        if not qs.exists() or update:

            if not instance.can_update_from_crossref():
                return instance


            try:
                entry = instance.cleaned_crossref_response(doi)
            except HTTPError:
                # the given doi is not housed in crossref, lets
                # try get an updated bibtex string from doi.org
                # ACTUALLY THIS DOESN'T WORK WELL IF THE DOI IS
                # A DATA PUBLICATION DOI AND NOT THE ARTICLE
                # E.G. PANGEAE PUBLICATIONS
                return
            except Exception as e:
                print(e)
                return

            # entry['bibtex'] = instance.query_doi_for_bibtex(doi)
            entry['label'] = instance.label
            pubform = PublicationForm(entry, instance=instance)

            if pubform.is_valid():
                pubform.save()
                return pubform.instance.pk
            else:
                print('Submission invalid')
                print(pubform.errors)
        
    def file(self, obj):
        if obj.pdf:
            return mark_safe(f'<a href="{obj.pdf.url}"><i class="fas fa-file-pdf fa-2x"></i></a>')
        else:
            return ""

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('author','keywords')

    def _keywords(self, obj):
        return u", ".join(o.name for o in obj.keywords.all())

class AuthorAdminMixin(admin.ModelAdmin):

    list_display = ['prefix','given', 'family','suffix','ORCID','authenticated_orcid','_publications']
    search_fields = ['family', 'given', 'ORCID']
    list_filter = ['authenticated_orcid',]

    def get_queryset(self, request):
        return (
        super().get_queryset(request)
        .prefetch_related('publications')
        .annotate(_publications=Count('publications'))
        )

    def _publications(self, object):
        return object._publications
    _publications.admin_order_field = '_publications'
    _publications.short_description  = _('Publications')

    def merge(self, request, qs):
        to_be_merged = [str(x) for x in qs]
        if len(to_be_merged) > 2:
            to_be_merged = f"{', '.join(to_be_merged[:-1])} and {to_be_merged[-1]}"
        else:
            to_be_merged = ' and '.join(to_be_merged)
        change_message = f"Merged {to_be_merged} into a single {qs.model._meta.verbose_name}"
        merged = MergedModelInstance.create(qs.first(),qs[1:],keep_old=False)
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(qs.model).pk,
            object_id=qs.first().pk,
            object_repr=str(qs.first()),
            action_flag=2, #CHANGE
            change_message=_(change_message),
        )
        self.message_user(request, change_message, messages.SUCCESS)

    merge.short_description = "Merge duplicate authors"
