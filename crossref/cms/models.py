from django.db import models
from cms.models.pluginmodel import CMSPlugin
from ..utils import get_publication_model
from django.utils.translation import gettext_lazy as _
from sortedm2m.fields import SortedManyToManyField

class Citation(CMSPlugin):

    type_choices = (
        ('p', _('Parentheses')),
        ('t', _('Textual')),
    )

    publication = SortedManyToManyField(get_publication_model())
    style = models.CharField(max_length=16, blank=True, null=True)
    type = models.CharField(max_length=1, choices=type_choices, default='p')
    hyperlink = models.BooleanField(default=True)