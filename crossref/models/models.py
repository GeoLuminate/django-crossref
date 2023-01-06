from django.db import models
from django.utils.translation import gettext as _, pgettext as _p
from sortedm2m.fields import SortedManyToManyField
from crossref.conf import settings
from datetime import timedelta as td
from django.utils import timezone
from django.urls import reverse
from django.db.models import F
from .fields import (
    ObjectField,
    StringArrayField,
    ObjectArrayField
)
from solo.models import SingletonModel
from crossref.conf import settings
from crossref.utils.choices import STYLE_CHOICES
from django.template.loader import render_to_string
from .managers import WorkQuerySet, AuthorQuerySet
from taggit.managers import TaggableManager
from filer.fields.file import FilerFileField


class Configuration(SingletonModel):

    default_style = models.CharField(_('default citation style'),
                                     help_text=_(
                                         'Determines the default style for both in-text citations and bibliography'),
                                     max_length=255,
                                     choices=STYLE_CHOICES,
                                     default=settings.CROSSREF_DEFAULT_STYLE)
    api_key = models.CharField(_('CrossRef API Key'),
                               help_text=_(
                                   'API key to send with each request. (currently does nothing)'),
                               max_length=255,
                               blank=True, null=True,
                               default=settings.CROSSREF_API_KEY)
    ua_string = models.CharField(max_length=255,
                                 blank=True, null=True,
                                 default=settings.CROSSREF_UA_STRING)

    def __str__(self):
        return _("Settings")

    class Meta:
        verbose_name = _("configuration")


class Subject(models.Model):
    name = models.CharField(_('name'),
                            unique=True,
                            max_length=255)

    class Meta:
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')
        ordering = ['name']

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)


class WorkAuthor(models.Model):
    """An intermediate table for the Work-Author m2m relationship.
    `SortedManyToManyField` automatically creates this table, however, there is no access via querysets. Defining here instead allows us to have access to the intermediate table in order to query author position.
    """
    work = models.ForeignKey("crossref.Work", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "crossref.Author",
        related_name='position',
        on_delete=models.CASCADE)
    number = models.IntegerField()

    _sort_field_name = 'number'

    def __str__(self):
        return str(self.number)


class Author(models.Model):
    objects = AuthorQuerySet.as_manager()

    prefix = models.CharField(
        _('prefix'),
        max_length=32,
        blank=True,
        null=True)
    given = models.CharField(
        _('given name'),
        max_length=64,
        blank=True,
        null=True)
    family = models.CharField(_('family name'), max_length=64, blank=True)
    suffix = models.CharField(
        _('suffix'),
        max_length=32,
        blank=True,
        null=True)
    ORCID = models.CharField("ORCID", max_length=64, blank=True, null=True)
    authenticated_orcid = models.BooleanField(
        _('ORCID is authenticated'), null=True, default=None)
    affiliation = ObjectArrayField(_('affiliation'),
                                   null=True, blank=True
                                   )

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')
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
        return reverse("literature:author_detail", kwargs={"pk": self.pk})

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
    """Model representation of CrossRef's Work endpoint."""

    objects = WorkQuerySet.as_manager()

    DOI = models.CharField(max_length=128,
                           verbose_name='DOI',
                           blank=True, null=True,
                           unique=True)
    ISBN = StringArrayField('ISBN',
                            help_text=_(
                                'Array of International Standard Serial Numbers (ISBNs)'),
                            blank=True, null=True)
    ISSN = StringArrayField('ISSN',
                            help_text=_(
                                'Array of International Standard Serial Numbers (ISBNs)'),
                            blank=True, null=True)
    URL = models.URLField(max_length=512,
                          verbose_name='URL',
                          blank=True, null=True,
                          unique=True)
    abstract = models.TextField(_('abstract'),
                                blank=True, null=True)
    author = SortedManyToManyField("crossref.Author",
                                   verbose_name=_('authors'),
                                   related_name='works',
                                   through=WorkAuthor,
                                   #    base_class=WorkAuthor,

                                   sort_value_field_name='position',
                                   blank=True)
    container_title = models.CharField(_('container title'),
                                       max_length=255,
                                       blank=True, null=True,)
    edition_number = models.CharField(_('edition number'),
                                      max_length=255,
                                      blank=True, null=True,)
    funder = ObjectArrayField(_('funders'),
                              null=True,
                              blank=True)
    institution = ObjectField(_('institution'),
                              null=True,
                              blank=True)
    is_referenced_by_count = models.PositiveSmallIntegerField(_('referenced by'),
                                                              blank=True,
                                                              null=True)
    isbn_type = ObjectArrayField(_('ISBN type'),
                                 help_text=_(
        'Array of objects that contain type and value of International Standard Book Numbers (ISBNs)'),
        blank=True, null=True)
    issn_type = ObjectArrayField(_('ISSN type'),
                                 help_text=_(
        'Array of objects that contain type and value of International Standard Serial Numbers (ISSNs)'),
        blank=True, null=True)
    issue = models.CharField(_('issue'),
                             max_length=16,
                             blank=True, null=True)
    language = models.CharField(_('language'),
                                max_length=16, blank=True, null=True)
    page = models.CharField(_('page'),
                            max_length=16,
                            blank=True, null=True)
    part_number = models.CharField(_('part number'),
                                   max_length=32,
                                   blank=True, null=True)
    published = models.DateField(_('date published'),
                                 null=True, blank=True)
    publisher = models.CharField(_('publisher'),
                                 max_length=255,
                                 blank=True, null=True)
    publisher_location = models.CharField(_('publisher location'),
                                          max_length=255,
                                          blank=True, null=True)
    reference_count = models.PositiveSmallIntegerField(_('reference count'),
                                                       blank=True, null=True)
    source = models.CharField(_('source'), max_length=64,
                              default='User Upload',
                              blank=True)
    subject = models.ManyToManyField("crossref.Subject",
                                     verbose_name=_('subjects'),
                                     blank=True)
    subtitle = models.CharField(_('subtitle'),
                                max_length=255,
                                blank=True, null=True)
    subtype = models.CharField(_('subtype'),
                               max_length=255,
                               blank=True, null=True)
    title = models.CharField(_('title'),
                             max_length=511,
                             blank=True, null=True)
    type = models.CharField(_('type'),
                            max_length=64,
                            blank=True, null=True)
    volume = models.CharField(_('volume'),
                              max_length=16,
                              blank=True, null=True)

    pdf = FilerFileField(
        verbose_name="PDF",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="literature_pdf")
    label = models.CharField(_('label'),
                             max_length=64,
                             blank=True)
    keywords = TaggableManager(verbose_name=_('key words'),
                               blank=True,
                               help_text=None)

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
        return ("title__icontains", "author__family__icontains",
                "label__icontains",)

    @property
    def year(self):
        return self.published.year if self.published else None

    @property
    def month(self):
        return self.published.strftime("%b")

    def author_string(self, et_al_after=None):
        """Converts a list of associated Author instances into a string of author names"""
        authors = self.author.all()
        author_count = authors.count()

        if author_count == 1:
            return str(authors.first())

        if et_al_after:
            return ", ".join(str(v) for v in authors[:et_al_after - 1])
        else:
            start = ", ".join(str(v) for v in authors[:-1])

            return f"{start} & {authors.last()}"

        return ""

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
        if self.crossref_last_queried and (
                timezone.now() - td(hours=24)) < self.crossref_last_queried:
            return False
        return True

    def bibliographic(self):
        style = Configuration.get_solo().default_style
        return render_to_string(
            f"crossref/styles/{style}/bibliography.html", {'pub': self})
