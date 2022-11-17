from xml.dom import ValidationErr
from django.db.models.query import QuerySet
from asgiref.sync import sync_to_async
from django.db import IntegrityError, transaction
from crossref.utils import query_and_clean_crossref
from django.forms import ValidationError
from django.db.models import (
    Q, Count, DateField,
    ExpressionWrapper, F,
    fields, Max)
from datetime import date, timedelta
from django.db.models.functions import Cast


class WorkQuerySet(QuerySet):

    def get_or_query_crossref(self, doi, **kwargs):
        """This is intended to mimic the `queryset.get_or_create` function on
        the default Django manager. However, it will try fetch the doi from
        CrossRef if it is not already in the database.

        Plain DOI's are stored in the database, therefore Django's `__in`
        filter is used to catch the case where a full uri is supplied
        instead of a plain DOI.


        Args:
            doi (_type_): _description_

        Returns:
            _type_: _description_
        """
        self._for_write = True
        try:
            # changing to lower case because doi is case insensitive
            return self.get(DOI=doi.lower()), False
        except self.model.DoesNotExist:
            # Try to fetch data from the crossref database
            validated_form = query_and_clean_crossref(
                doi, kwargs.pop('request', None))
            if validated_form.errors:
                doi_errors = validated_form.errors.get('DOI')
                if doi_errors:
                    if doi_errors.data[0].code == 'unique':
                        try:
                            return self.get(
                                DOI=validated_form.data['DOI']), False
                        except BaseException:
                            pass
                else:
                    # At this point, there are errors in some of the other
                    # fields
                    return validated_form, False
                    raise ValidationError(f'An error occured validating {doi}')
            try:
                with transaction.atomic(using=self.db):

                    return validated_form.save(), True
                    # return self.create(**cleaned_data), True
            except IntegrityError:
                try:
                    return self.get(DOI=doi), False
                except self.model.DoesNotExist:
                    pass
                raise

    async def aget_or_query_crossref(self, doi=None, **kwargs):
        return await sync_to_async(self.get_or_query_crossref)(
            doi=doi,
            **kwargs,
        )


class AuthorQuerySet(QuerySet):

    def with_work_counts(self):
        """Convenience filter for retrieving authors with annotated
        counts of works published as either lead or supporting author.

        These count attributes can be accessed on the queryset as
        `as_lead` or `as_supporting`. Further filtering/manipulation is
        possible on both fields afterwards.

        Example:
            Get authors that have published at least five works as
            lead author.

            >>> Author.objects.with_work_counts().filter(as_lead__gte=5)

            Get authors that have published only once but have been a supporting
            author on at least three.

            >>> Author.objects.with_work_counts().filter(as_lead=1, as_supporting__gte=3)
        """
        return (self.prefetch_related('works')
                .annotate(
                as_lead=Count(
                    'position', filter=Q(
                        position__number=1)),
                as_supporting=Count(
                    'position', filter=Q(
                        position__number__gt=1)),
                ))

    def as_lead(self):
        """Convenience filter for retrieving only authors that
        are listed as the lead author on a publication."""

        return (self.prefetch_related('works')
                .annotate(
                as_lead=Count(
                    'position', filter=Q(
                        position__number=1)))
                .filter(as_lead__gt=0)
                )

    def with_last_published(self):
        return (self.prefetch_related('works')
                .annotate(last_published=Max('works__published')))

    def is_active(self):
        cutoff = date.today() - timedelta(days=365.25 * 5)
        return (self.with_last_published()
                .filter(last_published__gt=cutoff))

    # def is_active(self):
    #     return (self.with_last_published()
    #         .annotate(
    #         is_active=ExpressionWrapper(
    #             Cast(timezone.now(), DateField()) - F('works__published'),
    #             output_field=fields.DurationField())))
