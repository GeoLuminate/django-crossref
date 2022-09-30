from xml.dom import ValidationErr
from django.db.models.query import QuerySet
from asgiref.sync import sync_to_async
from django.db import IntegrityError, transaction
from crossref.utils import query_and_clean_crossref
from django.forms import ValidationError

class WorkQuerySet(QuerySet):

    def get_or_query_crossref(self, doi, **kwargs):
        
        self._for_write = True
        try:
            # changing to lower case because doi is case insensitive
            return self.get(DOI=doi.lower()), False
        except self.model.DoesNotExist:
            # Try to fetch data from the crossref database
            validated_form = query_and_clean_crossref(doi,kwargs.pop('request',None))
            if validated_form.errors:
                doi_errors = validated_form.errors.get('DOI')
                if doi_errors:
                    if doi_errors.data[0].code == 'unique':
                        try:
                            return self.get(DOI=validated_form.data['DOI']), False
                        except:
                            pass
                # raise ValidationError(f'An error occured validating {doi}') 
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
        
        

        