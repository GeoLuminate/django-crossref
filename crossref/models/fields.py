from django.db.models import JSONField
from django.core import exceptions
from crossref.utils.validators import PythonTypeValidator


class ObjectField(JSONField):
    default_validators = [PythonTypeValidator(dict)]

    def __init__(self, verbose_name=None, validators=[],
                 item_validators=[], **kwargs):
        self.item_validators = item_validators
        super().__init__(verbose_name, validators, **kwargs)


class ArrayField(JSONField):
    default_validators = [PythonTypeValidator(list)]
    default_item_validators = []

    def __init__(self, verbose_name=None, validators=[],
                 item_validators=[], **kwargs):
        self.item_validators = item_validators
        super().__init__(verbose_name, validators=validators, **kwargs)

    def run_validators(self, value):
        super().run_validators(value)
        errors = []

        validators = self.default_item_validators + self.item_validators

        for v in validators:
            for val in value:
                try:
                    v(val)
                except exceptions.ValidationError as e:
                    if hasattr(e, 'code') and e.code in self.error_messages:
                        e.message = self.error_messages[e.code]
                    errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)


class StringArrayField(JSONField):
    default_item_validators = [PythonTypeValidator(str)]


class ObjectArrayField(JSONField):
    default_item_validators = [PythonTypeValidator(dict)]


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
