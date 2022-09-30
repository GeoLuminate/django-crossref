from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from .models import Citation
from .forms import CitationForm



@plugin_pool.register_plugin
class CitationPlugin(CMSPluginBase):
    module = _('Crossref')
    model = Citation
    render_template = "crossref/cms/citation.html"
    cache = False
    name = _('Citation')
    text_enabled = True
    form = CitationForm
    disable_child_plugins = True
    # require_parent = True

    raw_id_fields = ('work',)
    autocomplete_lookup_fields = {
        'm2m': ['work'],
    }

    def icon_alt(self, instance):
        return '<br>'.join([pub.title for pub in instance.work.all()])




@plugin_pool.register_plugin
class BibliographyPlugin(CMSPluginBase):
    module = _('Crossref')
    render_template = "crossref/cms/bibliography.html"
    cache = False
    name = _('Bibliography')