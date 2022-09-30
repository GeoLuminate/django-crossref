from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.core import exceptions
from .validators import PythonTypeValidator
from .widgets import PagesWidget

class ObjectField(JSONField):
    default_validators = [PythonTypeValidator(dict)]

    def __init__(self, verbose_name=None, validators=[], item_validators=[], **kwargs):
        self.item_validators = item_validators
        super().__init__(verbose_name, validators, **kwargs)


class ArrayField(JSONField):
    default_validators = [PythonTypeValidator(list)]

    def __init__(self, verbose_name=None, validators=[], item_validators=[], **kwargs):
        self.item_validators = item_validators
        super().__init__(verbose_name, validators=validators, **kwargs)

    def run_validators(self, value):
        super().run_validators(value)
        errors = []
        for v in self.item_validators:
            for val in value:
                try:
                    v(val)
                except exceptions.ValidationError as e:
                    if hasattr(e, 'code') and e.code in self.error_messages:
                        e.message = self.error_messages[e.code]
                    errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)


class ListConcatField(forms.CharField):

    def to_python(self, value):
        """Return a string from a list."""
        if value not in self.empty_values:
            if isinstance(value, list):
                value = ''.join(value)
            value = str(value)
            if self.strip:
                value = value.strip()
        if value in self.empty_values:
            return self.empty_value
        return value


class CrossRefAuthorField(forms.ModelMultipleChoiceField):

    # def _check_values(self, value):
    def prepare_value(self, value):
        """
        Given a list of author dicts (as returned by crossref), return a QuerySet of the corresponding objects. Values are queried on given and family name. A new object will be created if not found in the database already.
        """
        
        # handle the odd case where crossref entry doesn't have an author
        if not value:
            return
        
        authors = []

        for author in value:
            given = author.pop('given','').strip().replace(',','')
            family = author.pop('family','').strip().replace(',','')
            defaults = {k.replace('-','_'):v for k,v in author.items() if k.replace('-','_') in [f.name for f in self.queryset.model._meta.fields]}

            try:
                obj, _ = self.queryset.update_or_create(
                    given=given, 
                    family=family, 			
                    defaults=defaults)

            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages['invalid_author'],
                    code='invalid_author',
                    params=author,
                )
            authors.append(obj.id)

        # return self.queryset.filter(id__in=authors)
        return authors


class BibtexAuthorField(forms.ModelMultipleChoiceField):

    def prepare_value(self, value):
        if value:
            value = value.split(' and ')
        return super().prepare_value(value)

    def _check_values(self, value):
        """
        Given a list of author dicts (as returned by crossref), return a QuerySet of the corresponding objects. Values are queried on given and family name. A new object will be created if not found in the database already.
        """
  
        authors = []
        for a in value:
            
            # this is not a very good way but oh well
            author = {k:v.strip().replace(',','') for k, v in zip(['family','given',], a.split(' '))}

            try:
                obj, _ = self.queryset.get_or_create(**author)
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages['invalid_author'],
                    code='invalid_author',
                    params=author,
                )
            authors.append(obj.id)

        return authors


class DatePartsField(forms.DateField):

    def to_python(self, value):	
        """
        Validate that the input can be converted to a date. Return a Python
        datetime.date object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, dict):
            if 'date-parts' in value.keys():
                date_parts = value['date-parts'][0]
                while len(date_parts) < 3:
                    date_parts.append(1)
                return datetime.date(*date_parts)
                # date_parts = {k: v for k,v in zip(['year','month','day'],value['date-parts'][0])}

        return super().to_python(value)


class PageField(forms.MultiValueField):
    """Form field for validating a page range"""
    widget = PagesWidget

    def __init__(self, **kwargs):
        # Or define a different message for each field.
        fields = (forms.CharField(), forms.CharField())
        super().__init__(fields=fields,
            require_all_fields=False, required=False
        )

    def validate(self, value):
        print(value)

    def compress(self, data_list):
        return "-".join(data_list)

CROSSREF_WORK_FIELDS = {
  "institution": {
    "$ref": "#/definitions/WorkInstitution"
  },
  "indexed": {
    "$ref": "#/definitions/Date"
  },
  "posted": {
    "$ref": "#/definitions/DateParts"
  },
  "publisher-location": {
    "type": "string"
  },
  "update-to": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkUpdate"
    }
  },
  "standards-body": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkStandardsBody"
    }
  },
  "edition-number": {
    "type": "string"
  },
  "group-title": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "reference-count": {
    "type": "integer",
    "format": "int64"
  },
  "publisher": {
    "type": "string"
  },
  "issue": {
    "type": "string"
  },
  "isbn-type": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkISSNType"
    }
  },
  "license": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkLicense"
    }
  },
  "funder": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkFunder"
    }
  },
  "content-domain": {
    "$ref": "#/definitions/WorkDomain"
  },
  "chair": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/Author"
    }
  },
  "short-container-title": {
    "type": "string"
  },
  "accepted": {
    "$ref": "#/definitions/DateParts"
  },
  "content-updated": {
    "$ref": "#/definitions/DateParts"
  },
  "published-print": {
    "$ref": "#/definitions/DateParts"
  },
  "abstract": {
    "type": "string"
  },
  "DOI": {
    "description": "The DOI identifier associated with the work",
    "type": "string"
  },
  "type": {
    "type": "string"
  },
  "created": {
    "$ref": "#/definitions/Date"
  },
  "approved": {
    "$ref": "#/definitions/DateParts"
  },
  "page": {
    "type": "string"
  },
  "update-policy": {
    "type": "string"
  },
  "source": {
    "type": "string"
  },
  "is-referenced-by-count": {
    "type": "integer",
    "format": "int64"
  },
  "title": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "prefix": {
    "type": "string"
  },
  "volume": {
    "type": "string"
  },
  "clinical-trial-number": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkClinicalTrial"
    }
  },
  "author": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/Author"
    }
  },
  "member": {
    "type": "string"
  },
  "content-created": {
    "$ref": "#/definitions/DateParts"
  },
  "published-online": {
    "$ref": "#/definitions/DateParts"
  },
  "reference": {
    "$ref": "#/definitions/Reference"
  },
  "container-title": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "review": {
    "$ref": "#/definitions/WorkReview"
  },
  "original-title": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "language": {
    "type": "string"
  },
  "link": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkLink"
    }
  },
  "deposited": {
    "$ref": "#/definitions/Date"
  },
  "score": {
    "type": "integer",
    "format": "int64"
  },
  "degree": {
    "type": "string"
  },
  "subtitle": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "translator": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/Author"
    }
  },
  "free-to-read": {
    "$ref": "#/definitions/WorkFreeToRead"
  },
  "editor": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/Author"
    }
  },
  "component-number": {
    "type": "string"
  },
  "short-title": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "issued": {
    "$ref": "#/definitions/DateParts"
  },
  "ISBN": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "references-count": {
    "type": "integer",
    "format": "int64"
  },
  "part-number": {
    "type": "string"
  },
  "journal-issue": {
    "$ref": "#/definitions/WorkJournalIssue"
  },
  "alternative-id": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "URL": {
    "type": "string"
  },
  "archive": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "relation": {
    "$ref": "#/definitions/WorkRelation"
  },
  "ISSN": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "issn-type": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkISSNType"
    }
  },
  "subject": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "published-other": {
    "$ref": "#/definitions/DateParts"
  },
  "published": {
    "$ref": "#/definitions/DateParts"
  },
  "assertion": {
    "type": "array",
    "items": {
      "$ref": "#/definitions/WorkAssertion"
    }
  },
  "subtype": {
    "type": "string"
  },
  "article-number": {
    "type": "string"
  }
}



CROSSREF_WORK_SELECTS = [
    'DOI',
    'ISBN',
    'ISSN',
    'URL',
    'abstract',
    'accepted',
    'alternative-id',
    'approved',
    'archive',
    'article-number',
    'assertion',
    'author',
    'chair',
    'clinical-trial-number',
    'container-title',
    'content-created',
    'content-domain',
    'created',
    'degree',
    'deposited',
    'editor',
    'event',
    'funder',
    'group-title',
    'indexed',
    'is-referenced-by-count',
    'issn-type',
    'issue',
    'issued',
    'license',
    'link',
    'member',
    'original-title',
    'page',
    'posted',
    'prefix',
    'published',
    'published-online',
    'published-print',
    'publisher',
    'publisher-location',
    'reference',
    'references-count',
    'relation',
    'score',
    'short-container-title',
    'short-title',
    'standards-body',
    'subject',
    'subtitle',
    'title',
    'translator',
    'type',
    'update-policy',
    'update-to',
    'updated-by',
    'volume',
]