from django import forms
from crossref.conf import settings
from .models import Citation

class CitationForm(forms.ModelForm):
    # style = forms.ChoiceField(choices=settings.CROSSREF_CMS_STYLES)

    class Meta:
        model = Citation
        fields = "__all__"
        