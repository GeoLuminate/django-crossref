import importlib
from django.conf import settings
from django.apps import apps 
from django.core.exceptions import ImproperlyConfigured
from pydoc import locate

def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


def get_app_dependency():
   # locate() returns None if the class is not found,
   # so you could return a default class instead if you wished.
   return locate(settings.MY_APP_DEPENDENCY)


def get_publication_model():
    """Return the Publication model that is active in this project."""
    model_str = settings.CROSSREF_MODELS.get('publication')
    try:
        return apps.get_model(model_str, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("CROSSREF_MODELS['publication'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "CROSSREF_MODELS['publication'] refers to model '%s' that has not been installed" % model_str
        )

def get_author_model():
    """Return the Author model that is active in this project."""
    model_str = settings.CROSSREF_MODELS.get('author')
    try:
        return apps.get_model(model_str, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("CROSSREF_MODELS['author'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "CROSSREF_MODELS['author'] refers to model '%s' that has not been installed" % model_str
        )