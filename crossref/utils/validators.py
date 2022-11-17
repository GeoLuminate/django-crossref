from lib2to3.pytree import Base
from django.utils.translation import gettext_lazy as _
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
import json
from django.core.exceptions import ValidationError


def validate_json(value):
    try:
        json.dumps(value)
    except TypeError:
        raise ValidationError("The given value is not valid json")


class ExactValidator(BaseValidator):
    def compare(self, a, b):
        return a is b


@deconstructible
class PythonTypeValidator(ExactValidator):
    message = _(
        'Ensure this value has at most %(python_type)d character/element (it has %(show_value)d).')
    code = 'python_type'

    def clean(self, x):
        return type(x)


@deconstructible
class LengthValidator(ExactValidator):
    message = _(
        'Ensure the length of this value is exactly %(length_value)d (it is %(show_value)d).')
    code = 'length_value'

    def clean(self, x):
        return len(x)
