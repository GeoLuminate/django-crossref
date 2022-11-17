# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import transaction
from django.template import Template, RequestContext
from django.http import HttpRequest
from crossref.models import Work, Author
from .data import FUNDER, WORK
from crossref.forms.forms importCrossRefWorkForm, FunderQuickAddForm

User = get_user_model()


class TestWork(TestCase):

    @classmethod
    def setUpTestData(cls):
        f = CrossRefWorkForm(WORK)
        if f.is_valid():
            f.save()

    def setUp(self):
        self.pub = Work.objects.first()

    def test_num_authors_saved(self):
        self.assertEqual(Author.objects.count(), 3)

    def test_year_method(self):
        self.assertEqual(self.pub.year, 2019)

    def test_month_method(self):
        self.assertEqual(self.pub.month, 'Aug')

    def test_work_str_method(self):
        self.assertEqual(self.pub.label, 'Jennings2019')

    # def test_add_from_crossref_url(self):
    #     self.assertEqual(self.client.get('/admin/crossref/work/add-from-crossref', follow=True).status_code, 200)

    # def test_import_bibtex_url(self):
        # 	self.assertEqual(self.client.get('/admin/crossref/work/import-bibtex', follow=True).status_code, 200)


class TestWork(TestCase):

    @classmethod
    def setUpTestData(cls):
        f = CrossRefWorkForm(WORK)
        if f.is_valid():
            f.save()

    def setUp(self):
        self.pub = Work.objects.first()
