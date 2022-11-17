from django import forms
from django.utils.translation import gettext_lazy as _
from .fields import (
    ListConcatField,
    CrossRefAuthorField,
    DatePartsField,
    BibtexAuthorField,
    PageField,
    ModelMultiChoiceCreate,
    InstitutionBibtexField,
)
from .. import utils
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from ..models import Subject
from itertools import chain

Work = utils.get_work_model()
Author = utils.get_author_model()


class APIResponseFormMixin():
    """A Django form mixin that modifies input data by converting from
    '-' seperated keys (as commonly used in JSON data) to unerscore separated
    keys (as usually found in Python structures)"""

    def full_clean(self):
        self.data = self.recursive_key_replace(self.data, '-', '_')
        return super().full_clean()

    def recursive_key_replace(self, input_dict, token, replace_with):
        """Recursively replaces dict keys using python's str.replace method

        Args:
            input_dict (dict): starting dict
            token (str): the string to be replaced in each key
            replace_with (str): the string to replace the token

        Returns:
            dict: A new dict with modified keys
        """
        output = {}
        for k, v in input_dict.items():
            k = k.replace(token, replace_with)
            if isinstance(v, dict):
                output[k] = self.recursive_key_replace(v, token, replace_with)
            else:
                output[k] = v
        return output


class FunderQuickAddForm(forms.Form):
    search = forms.ChoiceField()


class UploadForm(forms.Form):

    file = forms.FileField(
        label='Select a .bib file',
        required=True,
        widget=forms.FileInput(attrs={'hidden': True}),
    )


class WorkAdminForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = '__all__'
        field_classes = {
            'page': PageField,
        }


"""Forms for handling data returned from the CrossRef API"""


class CrossRefWorkForm(APIResponseFormMixin, forms.ModelForm):
    """Handles data returned from api.crossref.org/works/<doi>/ and
    validates against the `crossref.Work` model."""
    subject = ModelMultiChoiceCreate(
        Subject.objects.all(), to_field_name='name', required=False)

    class Meta:
        model = Work
        fields = '__all__'
        field_classes = {
            'title': ListConcatField,
            'subtitle': ListConcatField,
            'container_title': ListConcatField,
            'author': CrossRefAuthorField,
            'published': DatePartsField,
        }

    def _save_m2m(self):
        """
        Save the many-to-many fields and generic relations for this form.
        """
        cleaned_data = self.cleaned_data
        exclude = self._meta.exclude
        fields = self._meta.fields
        opts = self.instance._meta
        # Note that for historical reasons we want to include also
        # private_fields here. (GenericRelation was previously a fake
        # m2m field).
        for f in chain(opts.many_to_many, opts.private_fields):
            if not hasattr(f, "save_form_data"):
                continue
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if f.name in cleaned_data:
                f.save_form_data(self.instance, cleaned_data[f.name])


class CrossRefAuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = "__all__"


class CrossRefForm(forms.Form):
    DOI = forms.ChoiceField()

    class Media:
        css = {
            "all": ("https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",),
        }

        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js",
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',)


class DOIForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = ['DOI']


class BibtexForm(forms.ModelForm):

    year = forms.IntegerField(required=False)
    month = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)

    class Meta:
        model = Work
        fields = '__all__'
        field_classes = {
            'author': BibtexAuthorField,
            'institution': InstitutionBibtexField,
        }

        mapping = {
            "doi": "DOI",
            "url": "URL",
            "pages": "page",
            "number": "issue",
            "ENTRYTYPE": "type",
            "ID": "label",
            "journal": "container_title",
            "booktitle": "title",
        }

    def full_clean(self):
        data = {}
        for k, v in self.data.items():
            if k in self.Meta.mapping.keys():
                data[self.Meta.mapping[k]] = v
            else:
                data[k] = v

        self.data = data

        return super().full_clean()

    def clean_published(self):
        year = self.data.get('year', None)
        month = self.data.get('month', 1)
        day = self.data.get('day', 1)
        if year:
            try:
                return date(int(year), int(month), int(day))
            except ValueError as e:
                # reraise ValueError as ValidationError so that form
                # validation catches it
                raise ValidationError(e)

    def clean_type(self):
        work_type = self.cleaned_data.get('type')
        if work_type:
            return slugify(work_type)

    def clean(self):

        letters = 'abcdefghijklmnop'
        label = self.cleaned_data['label']
        authors = self.cleaned_data.get('author')
        published = self.cleaned_data.get('published')

        if label == 'PMCID' and authors and published:
            # build a label from first author's last name and year
            # of publication
            first_author = Author.objects.get(id=authors[0])
            self.cleaned_data['label'] = f"{first_author.family}_{published.year}"

        #     # We don't want label clashes so find how many labels already
        #     # in the database start with our new label then append the
        #     # appropriate letter.

        #     count = self._meta.model.objects.filter(
        #         label__contains=label).count()
        #     if count:
        #         label += letters[count + 1]
        #     self.cleaned_data['label'] = label

        return super().clean()
