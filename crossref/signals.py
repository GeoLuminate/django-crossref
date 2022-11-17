from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .utils import get_work_model
from django.db.models import Count
from .models import Funder

Work = get_work_model()


@receiver(pre_delete, sender=Work)
def remove_related_authors(sender, instance, **kwargs):
    """Removes all authors related to the (about-to-be) deleted work instance that are not
    associated with other works in the database."""
    instance.author.annotate(c=Count('works')).filter(c__lte=1).delete()
    # instance.funder.annotate(c=Count('works')).filter(c__lte=1).delete()
    instance.subject.annotate(c=Count('works')).filter(c__lte=1).delete()


@receiver(pre_save, sender=Funder)
def fetch_detailed_funder(sender, instance, *args, **kwargs):
    """Fetches detailed funder data from the Crossref API prior to saving.
    Useful when transferring funder objects from the Work model (which have
    limited information) to the Funder model."""
    pass
