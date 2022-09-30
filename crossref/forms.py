from django import forms
from django.utils.translation import gettext_lazy as _
from .fields import ListConcatField, CrossRefAuthorField, DatePartsField, BibtexAuthorField, PageField
from django.forms import Textarea, Select
from .widgets import CrossRefWorkWidget, CrossRefFunderWidget, PagesWidget
from . import utils

Work = utils.get_work_model()

class FunderQuickAddForm(forms.Form):
    search = forms.ChoiceField(widget=CrossRefFunderWidget())


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

class WorkForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = '__all__'
        field_classes = {
            'title': ListConcatField,
            'container_title': ListConcatField,
            'author': CrossRefAuthorField,
            'published': DatePartsField,
        }

    def full_clean(self):
        self.data = {k.replace('-','_'):v for k,v in self.data.items()}
        return super().full_clean()

    def clean(self):
        Author = utils.get_author_model()
        
        letters = 'abcdefghijklmnop'
        authors = self.cleaned_data['author']
        
        # if a label wasn't supplied with the bibtex file
        if authors and not self.cleaned_data.get('label'):
            # build a label from first author's last name and year
            # of publication
            first_author = Author.objects.get(id=self.cleaned_data['author'][0].id)
            year_published = self.cleaned_data['published'].year
            label = f"{first_author.family}{year_published}"

            # We don't want label clashes so find how many labels already
            # in the database start with our new label then append the 
            # appropriate letter.
            count = self._meta.model.objects.filter(label__contains=label).count()
            if count:
                label += letters[count+1]
            self.cleaned_data['label'] = label
    
        return super().clean()

    # def append_letter(self, value):
    #     """If the given query returns matches in the database. A letter will be 
    #     appended to maintain uniqueness.

    #     Args:
    #         query (_type_): _description_
    #     """
    #     letters = 'abcdefghijklmnop'
    #     count = self._meta.model.objects.filter(label__contains=label).count()
    #     if count:
    #         label += letters[count+1]


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

    class Meta:
        model = Work
        fields = '__all__'
        field_classes = {
            'author': BibtexAuthorField,
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

    def clean(self):
        Author = utils.get_author_model()
        
        letters = 'abcdefghijklmnop'
        authors = self.cleaned_data['author']
        
        # if a label wasn't supplied with the bibtex file
        if authors and not self.cleaned_data.get('label'):

            # build a label from first author's last name and year
            # of publication
            first_author = Author.objects.get(id=self.cleaned_data['author'][0])
            year_published = self.cleaned_data['published'].year
            label = f"{first_author.family}{year_published}"

            # We don't want label clashes so find how many labels already
            # in the database start with our new label then append the 
            # appropriate letter.

            count = self._meta.model.objects.filter(label__contains=label).count()
            if count:
                label += letters[count+1]
            self.cleaned_data['label'] = label
    
        return super().clean()


# from pprint import pprint

# entry = {
#     'eprint': 'https://academic.oup.com/gji/article-pdf/219/2/1377/29717570/ggz376.pdf', 'url': 'https://doi.org/10.1093/gji/ggz376', 'doi': '10.1093/gji/ggz376', 'issn': '0956-540X', 'abstract': '{Thermal conductivity is a physical parameter crucial to accurately estimating temperature and modelling thermally related processes within the lithosphere. Direct measurements are often impractical due to the high cost of comprehensive sampling or inaccessibility and thereby require indirect estimates. In this study, we report 340 new thermal conductivity measurements on igneous rocks spanning a wide range of compositions using an optical thermal conductivity scanning device. These are supplemented by a further 122 measurements from the literature. Using major element geochemistry and modal mineralogy, we produce broadly applicable empirical relationships between composition and thermal conductivity. Predictive models for thermal conductivity are developed using (in order of decreasing accuracy) major oxide composition, CIPW normative mineralogy and estimated modal mineralogy.Four common mixing relationships (arithmetic, geometric, square-root and harmonic) are tested and, while results are similar, the geometric model consistently produces the best fit. For our preferred model, \\\\$k\\_\\\\{\\\\text\\\\{eff\\\\}\\\\} = \\\\exp ( 1.72 \\\\, C\\_\\\\{\\\\text\\\\{SiO\\\\}\\_2\\\\} + 1.018 \\\\, C\\_\\\\{\\\\text\\\\{MgO\\\\}\\\\} - 3.652 \\\\, C\\_\\\\{\\\\text\\\\{Na\\\\}\\_2\\\\text\\\\{O\\\\}\\\\} - 1.791 \\\\, C\\_\\\\{\\\\text\\\\{K\\\\}\\_2\\\\text\\\\{O\\\\}\\\\})\\\\$, we find that SiO2 is the primary control on thermal conductivity with an RMS of 0.28\xa0W\xa0m−1\xa0K−1or ∼10\u2009per\u2009cent. Estimates from normative mineralogy work to a similar degree but require a greater number of parameters, while forward and inverse modelling using estimated modal mineralogy produces less than satisfactory results owing to a number of complications. Using our model, we relate thermal conductivity to both P-wave velocity and density, revealing systematic trends across the compositional range. We determine that thermal conductivity can be calculated from P-wave velocity in the range 6–8\xa0km\xa0s−1\xa0to within 0.31\xa0W\xa0m−1\xa0K−1\xa0using \\\\$k(\\\\{V\\_p\\\\}) = 0.5822 \\\\, V\\_p^2 - 8.263 \\\\, V\\_p + 31.62\\\\$. This empirical model can be used to estimate thermal conductivity within the crust where direct sampling is impractical or simply not possible (e.g. at great depths). Our model represents an improved method for estimating lithospheric conductivity than present formulas which exist only for a limited range of compositions or are limited by infrequently measured parameters.}', 'month': '08', 'year': '2019', 'pages': '1377-1394', 'number': '2', 'volume': '219', 'journal': 'Geophysical Journal International', 'title': '{A new compositionally based thermal conductivity model for plutonic rocks}', 'author': 'Jennings, S and Hasterok, D and Payne, J', 'ENTRYTYPE': 'article'}
    
  

# form = BibtexForm(entry)
# form.is_valid()
# x=8