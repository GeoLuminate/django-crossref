from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .utils import get_work_model
from django.db.models import Count

Work = get_work_model()


@receiver(pre_delete, sender=Work)
def remove_related_authors(sender, instance, **kwargs):
    """Removes all authors related to the (about-to-be) deleted work instance that are not
    associated with other works in the database."""
    instance.author.annotate(c=Count('works')).filter(c__lte=1).delete()
    # instance.funder.annotate(c=Count('works')).filter(c__lte=1).delete()
    instance.subject.annotate(c=Count('works')).filter(c__lte=1).delete()
