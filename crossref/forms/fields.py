from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.core import exceptions
from django.forms import modelform_factory
from ..utils.validators import PythonTypeValidator, validate_json
from ..widgets import PagesWidget
from ..utils import get_author_model
from django.utils.encoding import force_str


class ListConcatField(forms.CharField):
    # class ListConcatField(forms.JSONField):
    """Accepts a json array input containing only strings and joins the
    items together using the specified `join_with` parameters.

    Args:
        forms (_type_): _description_
    """
    default_validators = [validate_json, PythonTypeValidator(list)]

    def to_python(self, value):
        value = ''.join(value)
        return super().to_python(value)


class InstitutionBibtexField(forms.JSONField):
    """Form field that converts bibtex institution field (str) into a dict
    with a single key called 'name' for compatibility with the Crossref
    institution field."""

    def to_python(self, value):
        if value is not None:
            value = {'name': value}
        return super().to_python(value)


class ModelMultipleFromJsonField(forms.ModelMultipleChoiceField):

    def prepare_value(self, value):
        """Takes a list of python dicts and uses modelform_factory
        to clean each and validate against the field's model.

        Args:
            value (list): A list of python dicts containing form data

        Raises:
            ValidationError: If the form fails to validate

        Returns:
            list: A list of ids of the saved entries
        """
        if not value:
            return

        model = self.queryset.model

        objs = []
        for obj in value:
            obj = self.modify_obj(obj)
            form = modelform_factory(model, fields="__all__")(obj)

            if form.is_valid():
                data = {k: v for k, v in form.cleaned_data.items() if v}
                if data.get('given') and data.get('family'):
                    try:
                        instance, _ = model.objects.update_or_create(
                            given=data.pop('given'),
                            family=data.pop('family'),
                            defaults=data,
                        )
                    except model.MultipleObjectsReturned:
                        instance = form.save()

                    objs.append(instance.id)
            else:
                raise ValidationError(
                    self.error_messages[f'invalid_{model._meta.model_name}'],
                    code=f'invalid_{model._meta.model_name}',
                    params=obj)
        return objs

    def init_instance(self, cleaned_data):
        """Takes cleaned data from the form and uses get_or_create to
        either fetch an instance from the database or create a new one.

        Args:
            cleaned_data (_type_): _description_

        Returns:
            _type_: _description_
        """
        instance = None
        return instance

    def modify_obj(self, obj):
        return obj


class ModelMultiChoiceCreate(forms.ModelMultipleChoiceField):
    """A subclass of `forms.ModelMultipleChoiceField` that ensures
    given values are added to the database if they do not already exist"""

    def prepare_value(self, value):
        if value is None:
            return value
        value = super().prepare_value(value)
        key = self.to_field_name or "pk"
        for v in value:
            self.queryset.get_or_create(**{key: v})
        return super().prepare_value(value)


class CrossRefAuthorField(ModelMultipleFromJsonField):
    """Given a list of author dicts (as returned by crossref), return a QuerySet of the corresponding objects. Values are queried on given and family name. A new object will be created if not found in the database already."""

    def modify_obj(self, obj):
        if obj.get('given'):
            obj['given'] = obj['given'].replace(
                ',', '').replace('.', '').strip()
        return obj

    def prepare_value(self, value):
        # hacky but the only way I could think to get access to this variable
        #  `clean` without running this method again.
        self.authors = super().prepare_value(value)
        return self.authors

    def clean(self, value):
        queryset = super().clean(value)
        if self.authors is None or not hasattr(queryset, '__iter__'):
            return queryset
        key = self.to_field_name or 'pk'

        objects = dict((force_str(getattr(o, key)), o) for o in queryset)

        for o in queryset:
            pass

        return [objects[force_str(val)] for val in self.authors]

    def has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = [force_str(value)
                       for value in self.prepare_value(initial)]
        data_set = [force_str(value) for value in data]
        return data_set != initial_set


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
            author = {k: v.strip().replace(',', '')
                      for k, v in zip(['family', 'given', ], a.split(' '))}

            try:
                # obj, _ = self.queryset.get_or_create(**author)
                obj = self.queryset.create(**author)
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
            if 'date_parts' in value.keys():
                date_parts = value['date_parts'][0]
                while len(date_parts) < 3:
                    date_parts.append(1)
                return datetime.date(*date_parts)

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
