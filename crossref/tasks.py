from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.translation import gettext_lazy as _
from .utils import get_work_model, query_crossref_for_doi


logger = get_task_logger(__name__)


@shared_task(name=_("Django Crossref: Update Work Counts"))
def retrieve_updated_work_counts():
    """Retrieve updated counts (is-referenced-by-count, references-count) for all Work entries
    sourced from the Crossref API."""
    Work = get_work_model()

    # get all Work objects where data was populated from the Crossref API
    qs = Work.objects.filter(source='Crossref').values_list('DOI', flat=True)
    for instance in qs:
        data = query_crossref_for_doi(instance.DOI)


@shared_task(name=_("Django Crossref: Import Bibtex"))
def import_bibtex_from_file(request, form):
    # TODO devise a way to schedule bibtex import
    # Requires the ability to store a results object to be viewed later.
    pass


@shared_task
def sample_task():
    logger.info("The sample task just ran.")
