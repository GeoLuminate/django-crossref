from django import forms
from django.utils.translation import gettext_lazy as _
from .fields import ListConcatField, CrossRefAuthorField, DatePartsField
from django.forms import Textarea
from .utils import get_publication_model


class UploadForm(forms.Form):
    
    file = forms.FileField(
        label='Select a .bib file',
        required=True)

class PublicationForm(forms.ModelForm):

    class Meta:
        model = get_publication_model()
        fields = '__all__'
        field_classes = {
            'title': ListConcatField,
            'container_title': ListConcatField,
            'author': CrossRefAuthorField,
            'published': DatePartsField,
        }

class CrossRefForm(forms.ModelForm):

    class Meta:
        model = get_publication_model()
        fields = ['DOI']
        widgets = {
            'DOI': Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class DOIForm(forms.ModelForm):

    class Meta:
        model = get_publication_model()
        fields = ['DOI']
            

