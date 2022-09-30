from crossref.conf import settings
from django.apps import apps 
from django.core.exceptions import ImproperlyConfigured
from habanero import Crossref
from crossref.conf import settings
from django.contrib.sites.shortcuts import get_current_site

def get_config():
    return apps.get_model('crossref.Settings').get_solo()


def query_crossref_for_doi(doi, request=None):
    if not doi:
        return None
    config = get_config().get_solo()
    if request is not None:
        site = get_current_site(request)
    
    cr = Crossref(
            base_url = settings.CROSSREF_BASE_URL,
            api_key = config.api_key,
            mailto = settings.CROSSREF_MAILTO,
            ua_string = config.ua_string,
        )
    
    return cr.works(doi)

def query_and_clean_crossref(doi, request=None):
    from .forms import WorkForm
    response = query_crossref_for_doi(doi, request)
    if response:
        form = WorkForm(response['message'])
        form.is_valid()
        return form
    

def get_model(model_str, model):
    try:
        return apps.get_model(model_str, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(f"CROSSREF_MODELS['{model}'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            f"CROSSREF_MODELS['{model}'] refers to model {model_str} that has not been installed")


def get_work_model():
    """Return the Work model that is active in this project."""
    model_str = settings.CROSSREF_MODELS.get('work','crossref.Work')
    return get_model(model_str, 'work')

def get_author_model():
    """Return the Author model that is active in this project."""
    model_str = settings.CROSSREF_MODELS.get('author','crossref.author')
    return get_model(model_str, 'author')
