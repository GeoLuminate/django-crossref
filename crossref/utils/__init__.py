from crossref.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from habanero import Crossref
from django.contrib.sites.shortcuts import get_current_site
import os


def get_config():
    return apps.get_model('crossref.Configuration').get_solo()


def query_crossref_for_doi(doi, request=None):
    if not doi:
        return None
    config = get_config().get_solo()
    if request is not None:
        site = get_current_site(request)

    cr = Crossref(
        base_url=settings.CROSSREF_BASE_URL,
        api_key=config.api_key,
        mailto=settings.CROSSREF_MAILTO,
        ua_string=config.ua_string,
    )

    return cr.works(doi)


def query_and_clean_crossref(doi, request=None):
    from crossref.forms import CrossRefWorkForm
    response = query_crossref_for_doi(doi, request)
    if response:
        form = CrossRefWorkForm(response['message'])
        form.is_valid()
        return form


def _get_model(model_str, model):
    """Utility function used by `crossref.utils.get_work_model` and
    `crossref.utils.get_author_model` to get the correct models as
    specified in the application setting.

    Args:
        model_str (str): As accepted by `apps.get_model()`
        model (str): Label for the requested model (for informative error
        reporting)

    Raises:
        ImproperlyConfigured: If the settings are not correctly specified as
        "app_label.model" or the requested model in not installed

    Returns:
        django.db.models.Model: The requested model
    """
    try:
        return apps.get_model(model_str, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            f"CROSSREF_MODELS['{model}'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            f"CROSSREF_MODELS['{model}'] refers to model {model_str} that has not been installed")


def get_work_model():
    """
    Returns:
        Work: The active Work model for the current project."""
    model_str = settings.CROSSREF_MODELS.get('work', 'crossref.Work')
    return _get_model(model_str, 'work')


def get_author_model():
    """
    Returns:
        Author: The active Author model for the current project.
    """
    model_str = settings.CROSSREF_MODELS.get('author', 'crossref.author')
    return _get_model(model_str, 'author')


def pdf_upload_path(instance, filename):
    return 'publications/{0}/{1}'.format(instance, filename)


def append_label_letter(instance):
    """Takes a Work instance and auto-appends a letter to the label
    when clashes are found with other entries in the table.

    Args:
        instance (crossref.Work): An instance of `crossref.Work`
    """
    letters = 'abcdefghijklmnop'

    # if a label wasn't supplied with the bibtex file
    if instance.label and instance.published.year:
        label = f"{instance.authors.first().family}{instance.published.year}"

        # count the number of items that start with this label
        count = instance._meta.model.objects.filter(
            label__startswith=label).count()
        if count:
            label += letters[count]

        instance.label = label
    return instance


def get_citation_style_path():
    return os.path.join(
        settings.BASE_DIR, 'crossref/templates/crossref/styles')
