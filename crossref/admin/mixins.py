from django.contrib import admin
from django.utils.html import mark_safe
from django.urls import path
from ..forms.forms import DOIForm, UploadForm, WorkAdminForm
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.shortcuts import render
from requests.exceptions import HTTPError
from django.contrib import messages
from django.utils.html import mark_safe
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db import models
from crossref.widgets import AdminPDFWidget
from crossref.utils.resources import BibtexResource
from django.template.defaultfilters import pluralize
from .filters import HasORCID, AuthorType
# from django.contrib.sites import models


class ChangeListQuickAdd():
    """Django Admin mixin that adds a select2 input to the top of the
    list_view. Submission of the select2 box is via ajax to a user defined URL.
    """
    select2 = {}
    change_list_template = 'admin/crossref/quick_add.html'

    def changelist_view(self, request, extra_context={}):
        extra_context['select2'] = self.select2
        extra_context['select'] = self.get_model_fields()
        extra_context['doi_form'] = DOIForm()
        extra_context['bibtex_import_form'] = UploadForm()
        return super().changelist_view(request, extra_context)

    def get_model_fields(self):
        return [f.name.replace('_', '-')
                for f in self.model._meta.get_fields()]


class CrossRefMixin(ChangeListQuickAdd, admin.ModelAdmin):
    """Includes the necessary media files for querying CrossRef via Select2
    """
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
    """Default Django Admin setup for the `crossref.models.Work` model.

    note:
        These settings are mostly defined here https://docs.djangoproject.com/en/4.1/ref/contrib/admin/

    """
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

    list_display = ['pdf', 'article', 'label', 'title', 'container_title',
                    'is_referenced_by_count', 'published', 'issue', 'volume',
                    'page', 'type']

    list_filter = ['type', 'container_title', 'language', 'source', 'subject']
    search_fields = ('DOI', 'title', 'id', 'label')
    list_editable = ['pdf', ]
    fieldsets = [
        (None, {
            'fields': [
                'DOI',
                'pdf',
            ]}
         ),
        ('Bibliographic', {'fields': [
            ('type', 'published'),
            'title',
            # 'author',
            'container_title',
            'volume',
            'issue',
            'page',
            'abstract',
        ]}),
        ('Additional', {'fields': [
            'keywords',
            'language',
            'source',
        ]}),
    ]

    formfield_overrides = {
        models.FileField: {'widget': AdminPDFWidget},

    }

    class Media:
        css = {
            "all": (
                'crossref/css/filer_extra.min.css',
            )
        }
        js = (
            "https://kit.fontawesome.com/a08181010c.js",
            # 'crossref/js/pdfInput.js',
        )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('author')

    def get_urls(self):
        return [
            path('import-bibtex/', self.admin_site.admin_view(self.import_bibtex),
                 name='import_bibtex'),
            path('add-doi/', self.admin_site.admin_view(self.get_doi_or_query_crossref),
                 name='add_from_crossref'),
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
                    message = mark_safe("<br>".join(
                        e for e in form.errors['DOI']))
                self.message_user(request, message, messages.INFO)
        return HttpResponseRedirect('../')

    def _get_data_from_crossref(self, request, doi):
        """Private function that handles retrieving information when a doi
        is provided.

        Args:
            request (HTTPRequest): The request object passed through the Django Admin class
            doi (str): The doi to be queried

        Returns:
            instance: a saved Work instance or False
        """
        errors = []
        try:
            # first, check if the object already exists. If it does
            # do nothing and either retrieve the object from the database,
            # or query crossref for the info
            instance, created = self.get_queryset(
                request).get_or_query_crossref(doi)
        except HTTPError as e:
            # Something wen't wrong during the request to crossref
            errors.append(e)
            # return None so the calling function knows something went wrong
            return None

        if created:
            message = mark_safe(
                f"Succesfully added: {instance.bibliographic()}")
            self.message_user(request, message, messages.SUCCESS)
        else:
            message = f"{instance.DOI} already exists in this database"
            self.message_user(request, message, messages.INFO)

        return instance

    def import_errors(self, request, *args, **kwargs):
        return

    @method_decorator(require_POST)
    def import_bibtex(self, request, *args, **kwargs):
        """Admin view that handles user-uploaded bibtex files

        Returns:
            HttpResponseRedirect: redirects to model admins change_list
        """
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            importer = BibtexResource(form.cleaned_data['file'].file, request)
            importer.process()
            if importer.result.has_errors:
                return render(request,
                              'admin/crossref/import_results.html',
                              context={'result': importer.result})
            else:
                report = importer.result.counts()
                if report['crossref'] or report['bibtex']:
                    self.message_user(
                        request,
                        level=messages.SUCCESS,
                        message=f"Import finished with {report['crossref']} new entr{pluralize(report['crossref'], 'y,ies')} from the CrossRef API and {report['bibtex']} new entr{pluralize(report['bibtex'], 'y,ies')} parsed direct from the bibtex file")
                if report['skipped']:
                    self.message_user(
                        request,
                        level=messages.INFO,
                        message=f"{report['skipped']} existing entr{pluralize(report['skipped'], 'y,ies')} were skipped during the import process")
        else:
            self.message_user(request,
                              'The uploaded file could not be validated',
                              level=messages.ERROR)
        return HttpResponseRedirect('../')

    def article(self, obj):
        if obj.DOI:
            return mark_safe(
                '<a href="https://doi.org/{}"><i class="fas fa-globe"></i></a>'.format(obj.DOI))
        else:
            return ''

    def file(self, obj):
        if obj.pdf:
            return mark_safe(
                f'<a href="{obj.pdf.url}"><i class="fas fa-file-pdf fa-2x"></i></a>')
        else:
            return ""


class AuthorAdminMixin(CrossRefMixin):
    """Default Django Admin setup for the `crossref.models.Author` model.

    note:
        These settings are mostly defined here https://docs.djangoproject.com/en/4.1/ref/contrib/admin/

    """
    list_display = ['family', 'given', 'prefix', 'suffix',
                    'as_lead', 'as_supporting', 'orcid', '_affiliation']
    search_fields = ['family', 'given', 'ORCID']
    list_filter = [AuthorType, HasORCID]

    def get_queryset(self, request):
        return super().get_queryset(request).with_work_counts()

    def as_lead(self, object):
        return object.as_lead
    as_lead.admin_order_field = 'as_lead'
    as_lead.short_description = _('as lead')

    def as_supporting(self, object):
        return object.as_supporting
    as_supporting.admin_order_field = 'as_supporting'
    as_supporting.short_description = _('as supporting')

    def orcid(self, object):
        if object.ORCID:
            return mark_safe(
                f"<a href={object.ORCID}>{object.ORCID.split('/')[-1]}</a>")
    orcid.admin_order_field = 'ORCID'
    orcid.short_description = 'ORCID'

    def _affiliation(self, obj):
        if obj.affiliation:
            return "; ".join([x['name'] for x in obj.affiliation])
    _affiliation.admin_order_field = 'affiliation'
    _affiliation.short_description = _('affiliation')


class FunderAdminMixin(CrossRefMixin):
    """Default Django Admin setup for the `crossref.models.Funder` model."""

    select2 = {
        'endpoint': 'https://api.crossref.org/funders',
        'id': 'id',
        'text': 'name'
    }

    list_display = ['id', 'name', 'location', 'uri']
    search_fields = ['name', 'id', ]
    list_filter = ['location', ]
