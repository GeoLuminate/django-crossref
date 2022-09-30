from django.test import SimpleTestCase
from ..validators import PythonTypeValidator, LengthValidator

def validate(validator, against, value):
    validator = validator(against)
    val = validator.clean(value)
    return validator.compare(against, val)

class TestValidators(SimpleTestCase):

    def assertValid(self, validator, against, value):
        """Runs the clean method on value then the compare method"""
        self.assertTrue(validate(validator, against, value))

    def assertInvalid(self, validator, against, value):
        """Runs the clean method on value then the compare method"""
        self.assertFalse(validate(validator, against, value))

    def test_PythonTypeValidator_validation(self):
        self.assertValid(PythonTypeValidator, list, [1,2,3])
        self.assertInvalid(PythonTypeValidator, dict, [1,2,3])
        self.assertValid(PythonTypeValidator, dict, {'x':1})

    def test_LengthValidator_validation(self):
        self.assertValid(LengthValidator, 3, [1,2,3])
        self.assertValid(LengthValidator, 3, "abc")
        self.assertValid(LengthValidator, 1, {'x':1})
        self.assertInvalid(PythonTypeValidator, 1, [1,2,3])


