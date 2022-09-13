from django.db import models
from django.utils.translation import gettext as _, pgettext as _p
from sortedm2m.fields import SortedManyToManyField
from taggit.managers import TaggableManager
from django.conf import settings
from habanero import Crossref
import requests
from datetime import timedelta as td
from django.utils import timezone
from requests.exceptions import HTTPError
from django.utils.html import mark_safe
from django.urls import reverse
from django.db.models import F
from django_ckeditor_5.fields import CKEditor5Field

cr = Crossref(
        base_url=getattr(settings,"CROSSREF_BASE_URL", "https://api.crossref.org"),
        api_key=getattr(settings,"CROSSREF_API_KEY", None),
        mailto=getattr(settings,"CROSSREF_MAILTO", settings.DEFAULT_FROM_EMAIL),
        ua_string = getattr(settings,"CROSSREF_UA_STRING", None)
    )

class AuthorAbstract(models.Model):
    prefix = models.CharField(max_length=32, blank=True, null=True)
    given = models.CharField(max_length=64, blank=True, null=True)
    family = models.CharField(max_length=64, blank=True)
    suffix = models.CharField(max_length=32, blank=True, null=True)
    ORCID = models.CharField(max_length=64, blank=True, null=True)
    authenticated_orcid = models.BooleanField(null=True, default=None)
    
    class Meta:
        db_table='publication_author'
        verbose_name = _('author')
        verbose_name_plural =  _('authors')
        abstract = True
        ordering = ['family']
        
    def __str__(self):
        return self.name()
    
    @property
    def reverse(self):
        return f"{self.family}, {self.given}"

    @property
    def reverse_initial(self):
        return f"{self.family}, {self.given[0]}"

    def get_absolute_url(self):
        return reverse("publications:author_detail", kwargs={"pk": self.pk})

    @staticmethod
    def autocomplete_search_fields():
        return ("family__icontains", "given__icontains",)

    def name(self):
        """Returns John Smith"""
        return f"{self.given} {self.family}"

    def name_reverse(self):
        """Returns Smith, John"""
        return f"{self.family}, {self.given} "

    def given_init_family(self):
        """Returns J. Smith"""
        return f"{self.given[0]}. {self.family}"

    def family_given_init(self):
        """Returns Smith, J."""
        return f"{self.family}, {self.given[0]}."
    
class PublicationAbstract(models.Model):
    """Model representing a publication."""

    class Meta:
        verbose_name = _('publication')
        verbose_name_plural = _('publications')
        abstract = True
        ordering = [F('published').desc(nulls_last=True), 'label']
        
    pdf = models.FileField(upload_to='publications/', blank=True, null=True)

    DOI = models.CharField(max_length=128, 
        verbose_name='DOI', 
        blank=True, null=True,
        unique=True)
    URL = models.URLField(max_length=128, 
        verbose_name='URL', 
        blank=True, null=True,
        unique=True)

    label = models.CharField(_('label'), 
        max_length=64, 
        unique=True,
        blank=True)
    type = models.CharField(_('publication type'), 
        max_length=64, 
        blank=True, null=True)
    container_title = models.CharField(_('journal/book title'), 
        max_length=128, 
        blank=True, null=True,)
    title = models.CharField(_('title'), 
        max_length=512, 
        blank=True, null=True)
    author = SortedManyToManyField(settings.CROSSREF_MODELS.get('author'),
        verbose_name=_('authors'),
        related_name='publications', 
        sort_value_field_name='position',
        blank=True)
    published = models.DateField(_('date published'), 
        null=True, blank=True)
    year = models.PositiveSmallIntegerField(_('year'), 
        null=True, blank=True)
    month = models.CharField(_('month'), 
        max_length=16, 
        null=True, blank=True)
    issue = models.CharField(_p('journal issue','issue'), 
        max_length=16, 
        blank=True, null=True)
    volume = models.CharField(_p('journal volume','volume'), 
        max_length=16, 
        blank=True, null=True)
    page = models.CharField(_('page'), 
        max_length=16, 
        blank=True, null=True)
    keywords = TaggableManager(verbose_name=_('key words'), 
        blank=True, help_text=None)
    abstract = CKEditor5Field(blank=True)

    is_referenced_by_count = models.PositiveSmallIntegerField(_('cited by'), 
        blank=True, null=True)
    language = models.CharField(_('language'), 
        max_length=16, blank=True, null=True)
    source = models.CharField(_('source'), 
        max_length=16, blank=True, null=True)


    crossref_last_queried = models.DateTimeField(_('last Crossref query'), blank=True, null=True, editable=False)

    doi_queried = models.BooleanField(_('DOI has been queried'), default=False)

    def __str__(self):
        return self.label

    @staticmethod
    def autocomplete_search_fields():
        # For Django Grappelli related lookups
        return ("title__icontains", "author__family__icontains", "label__icontains",)

    @property
    def year(self):
        if self.published:
            return self.published.year

    @property
    def month(self):
        return self.published.strftime("%b")

    def authors_citation(self):
        truncate_after = 2
        authors = [f"{a.family}" for a in self.author.all()]
        if len(authors) > truncate_after:
            return f'{authors[0]} et. al.'
        elif len(authors) == 2:
            return ' & '.join(authors)
        else:
            return authors[0]

    def authors_bibliography_init(self):
        truncate_after = settings.CROSSREF_AUTHOR_TRUNCATE_AFTER
        authors = [f"{a.family_given_init()}" for a in self.author.all()]
        if len(authors) > truncate_after:
            start = ', '.join(authors[:-1])
            last = authors[-1]
            return f'{start} & {last}'
        elif len(authors) == 1:
            return authors[0]
        else:
            return ' & '.join(authors)

    def authors_display(self):
        return self.display_names(self.authors_list)

    def authors_display_family(self):
        return self.display_names([a.family for a in self.author.all()])

    def display_names(self, names=None):
        authors = []
        for author in self.author.all():
            authors.append(
                f"<a href={author.get_absolute_url()}>{author}</a>")
                
        return mark_safe(', '.join(authors))
        truncate_after = settings.CROSSREF_AUTHOR_TRUNCATE_AFTER
        if names is None:
            names = self.authors_list
            
        if len(names) > truncate_after:
            return f'{names[0]} & {len(names)-1} others'
        elif len(self.authors_list) > 1:
            return f'{", ".join(names[:-1])} & {names[-1]}'
        elif len(names) == 1:
            return names[0]
        else:
            return ""

    def author_admin_display(self):
        if len(self.authors_list) > 2:
            return '{} et. al.'.format(self.authors_list[0])
        elif len(self.authors_list) == 1:
            return self.authors_list[0]
        else:
            return ' & '.join(self.authors_list)

    @property
    def authors_list(self):
        return [str(f) for f in self.author.all()]

    def query_crossref(self, doi=None):
        # if doi is None or self.DOI:
        #     return 

        if doi is None:
            doi = self.DOI

        try:
            response = cr.works(doi)
            self.crossref_last_queried = timezone.now()
        except HTTPError as e:
            self.crossref_last_queried = timezone.now()
            raise e
        except Exception as e:
            raise e 

        return response

    def query_doi_for_bibtex(self, doi=None):

        if self.doi_queried:
            return self.bibtex

        headers = {"Accept":"application/x-bibtex"}
        response = requests.get(f"https://doi.org/{doi}", headers=headers)

        if response.ok:
            self.doi_queried = True
        return response.text

    def _get_fields(self):
        return [f.name for f in self._meta.fields] + ['author']

    def cleaned_crossref_response(self, doi=None):
        response = self.query_crossref(doi)

        # writing this out for clarity
        # crossref uses hyphens instead of underscores so convert   them all 
        if response is not None:
            entry = {}
            for k,v in response['message'].items():
                converted_key = k.replace('-','_')
                if converted_key in self._get_fields():
                    entry[converted_key] = v
            return entry


    def can_update_from_crossref(self):
        if self.crossref_last_queried and (timezone.now() - td(hours=24)) < self.crossref_last_queried: 
            return False
        return True
