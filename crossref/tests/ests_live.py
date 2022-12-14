# -*- coding: utf-8 -*-

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from time import sleep
from crossref.tests import tests
from crossref.models import Work

class LiveTests(LiveServerTestCase):
	fixtures = ['initial_data.json', 'test_data.json']
	urls = 'works.tests.urls'

	@classmethod
	def setUpClass(cls):
		options = webdriver.firefox.options.Options()
		options.add_argument('--headless')
		cls.selenium = webdriver.Firefox(options=options)
		super(LiveTests, cls).setUpClass()


	@classmethod
	def tearDownClass(cls):
		cls.selenium.quit()
		super(LiveTests, cls).tearDownClass()


	def setUp(self):
		User.objects.create_superuser('admin', 'admin@test.de', 'admin')

		# login
		self.selenium.get('{0}{1}'.format(self.live_server_url, '/admin/'))
		username_input = self.selenium.find_element_by_name("username")
		username_input.send_keys('admin')
		password_input = self.selenium.find_element_by_name("password")
		password_input.send_keys('admin')
		self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()


	def test_import_bibtex(self):
		count = Work.objects.count()

		self.selenium.get('{0}{1}'.format(self.live_server_url, '/admin/crossref/work/import_bibtex/'))
		bibliography_input = self.selenium.find_element_by_name("bibliography")
		bibliography_input.send_keys(tests.TEST_BIBLIOGRAPHY)
		self.selenium.find_element_by_xpath('//input[@value="Import"]').click()

		self.assertEqual(Work.objects.count() - count, tests.TEST_BIBLIOGRAPHY_COUNT)


	def test_import_bibtex_button(self):
		count = Work.objects.count()

		self.selenium.get('{0}{1}'.format(self.live_server_url, '/admin/crossref/work/'))
		self.selenium.find_element_by_link_text('Import BibTex').click()
		self.selenium.find_element_by_xpath('//input[@value="Import"]').click()
