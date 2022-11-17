from django.test import SimpleTestCase
from ..utils.validators import PythonTypeValidator, LengthValidator
from ..forms.fields import ArrayField, ObjectField, HomogenousArrayField


class TestFields(SimpleTestCase):

    def test_ArrayField_init(self):
        field = ArrayField()
        self.assertIsInstance(field, ArrayField)

    def test_ObjectField_init(self):
        field = ObjectField()
        self.assertIsInstance(field, ObjectField)

    def test_HomogenousArrayField_init(self):
        field = HomogenousArrayField()
        self.assertIsInstance(field, HomogenousArrayField)
