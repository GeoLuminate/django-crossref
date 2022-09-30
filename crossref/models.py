from django.db import models
from django.utils.translation import gettext as _, pgettext as _p
from sortedm2m.fields import SortedManyToManyField
from crossref.conf import settings
from habanero import Crossref
import requests
from datetime import timedelta as td
from django.utils import timezone
from requests.exceptions import HTTPError
from django.utils.html import mark_safe
from django.urls import reverse
from django.db.models import F

from .fields import ArrayField
from . import validators
from solo.models import SingletonModel
from crossref.conf import settings
from .choices import STYLE_CHOICES
from django.template.loader import render_to_string
from .managers import WorkQuerySet

class Settings(SingletonModel):
    
    default_style = models.CharField(_('default citation style'),
        help_text = _('Determines the default style for both in-text citations and bibliography'),
        max_length=255,
        choices=STYLE_CHOICES, 
        default=settings.CROSSREF_DEFAULT_STYLE)
    api_key = models.CharField(_('CrossRef API Key'),
        help_text = _('API key to send with each request. (currently does nothing)'),
        max_length=255, 
        blank=True, null=True, 
        default=settings.CROSSREF_API_KEY)
    ua_string = models.CharField(max_length=255,
        blank=True, null=True, 
        default=settings.CROSSREF_UA_STRING)

    def __str__(self):
        return _("Settings")

    class Meta:
        verbose_name = _("Settings")


class Author(models.Model):
    prefix = models.CharField(max_length=32, blank=True, null=True)
    given = models.CharField(max_length=64, blank=True, null=True)
    family = models.CharField(max_length=64, blank=True)
    suffix = models.CharField(max_length=32, blank=True, null=True)
    ORCID = models.CharField(max_length=64, blank=True, null=True)
    authenticated_orcid = models.BooleanField(null=True, default=None)
    
    class Meta:
        db_table='work_author'
        verbose_name = _('author')
        verbose_name_plural =  _('authors')
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
        return reverse("works:author_detail", kwargs={"pk": self.pk})

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
        if self.given:
            return f"{self.given[0]}. {self.family}"

    def family_given_init(self):
        """Returns Smith, J."""
        if self.given:       
            return f"{self.family}, {self.given[0]}."
        else:
            return self.family
    

class Work(models.Model):
    objects = WorkQuerySet.as_manager()
    
    """Model representing a work."""
    DOI = models.CharField(max_length=128, 
        verbose_name='DOI', 
        blank=True, null=True,
        unique=True)
    isbn_type = ArrayField(
        help_text=_('Array of objects that contain type and value of International Standard Book Numbers (ISBNs)'),
        blank=True, null=True)
    issn_type = ArrayField(
        help_text=_('Array of objects that contain type and value of International Standard Serial Numbers (ISSNs)'),
        blank=True, null=True)

    URL = models.URLField(max_length=128, 
        verbose_name='URL', 
        blank=True, null=True,
        unique=True)
    label = models.CharField(_('label'), 
        max_length=64, 
        unique=True,
        blank=True)
    type = models.CharField(_('work type'), 
        max_length=64, 
        blank=True, null=True)
    container_title = models.CharField(_('journal/book title'), 
        max_length=128, 
        blank=True, null=True,)
    title = models.CharField(_('title'), 
        max_length=512, 
        blank=True, null=True)
    author = SortedManyToManyField("crossref.Author",
        verbose_name=_('authors'),
        related_name='works', 
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
    abstract = models.TextField(blank=True, null=True)

    is_referenced_by_count = models.PositiveSmallIntegerField(_('cited by'), 
        blank=True, null=True)
    language = models.CharField(_('language'), 
        max_length=16, blank=True, null=True)

    source = models.CharField(max_length=128,
        default='User Upload',
        blank=True)

    last_queried_crossref = models.DateTimeField(_('last Crossref query'), 
                                                 blank=True, null=True, editable=False)

    class Meta:
        verbose_name = _('work')
        verbose_name_plural = _('works')
        ordering = [F('published').desc(nulls_last=True), 'label']
        default_related_name = 'works'

    def __str__(self):
        return self.label

    @staticmethod
    def autocomplete_search_fields():
        return ("title__icontains", "author__family__icontains", "label__icontains",)

    @property
    def year(self):
        return self.published.year if self.published else None

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

    def can_update_from_crossref(self):
        if self.crossref_last_queried and (timezone.now() - td(hours=24)) < self.crossref_last_queried: 
            return False
        return True

    def bibliographic(self):
        style = Settings.get_solo().default_style
        return render_to_string(f"crossref/styles/{style}/bibliography.html", {'pub': self})
   
    
class Funder(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    location = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    uri = models.URLField()
    alt_names = models.JSONField()
    replaces = models.JSONField(blank=True, null=True)
    replaced_by = models.JSONField(blank=True, null=True)
    tokens = models.JSONField()
    
    class Meta:
        verbose_name = _('funder')
        verbose_name_plural =  _('funders')
        
    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains", "id__iexact", )
