from django.test import SimpleTestCase
from ..models import Work, Author
from ..utils import (
    get_author_model,
    get_work_model,
)
from django.core.exceptions import ImproperlyConfigured

class TestFields(SimpleTestCase):

    def test_get_work_model(self):
        self.assertIs(get_work_model(), Work)
    
        # test ImproperlyConfigured is raised when a non-installed model is specified
        with self.settings(CROSSREF_MODELS={'work': 'non_installed_app.Work'}):
            self.assertRaises(ImproperlyConfigured, get_work_model)

        # test ImproperlyConfigured is raised when the model is not specified as app_label.model
        with self.settings(CROSSREF_MODELS={'work': 'Author'}):
            self.assertRaises(ImproperlyConfigured, get_work_model)
   
    def test_get_author_model(self):
        self.assertIs(get_author_model(), Author)

        # test ImproperlyConfigured is raised when a non-installed model is specified
        with self.settings(CROSSREF_MODELS={'author': 'non_installed_app.Author'}):
            self.assertRaises(ImproperlyConfigured, get_author_model)

        # test ImproperlyConfigured is raised when the model is not specified as app_label.model
        with self.settings(CROSSREF_MODELS={'author': 'Author'}):
            self.assertRaises(ImproperlyConfigured, get_author_model)