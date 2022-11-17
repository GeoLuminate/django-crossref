from . import query_crossref_for_doi, get_work_model
import json
from crossref.utils.parsers import bibtex
from io import TextIOWrapper
from tqdm import tqdm
from ..forms.forms import BibtexForm, CrossRefWorkForm
from requests.exceptions import HTTPError
from django.db import transaction
from django.db.models import Q


class BibtexEntry():

    def __init__(self, entry):
        self.data = entry
        self.messages = []
        self.status = ""

    def __str__(self):
        return json.dumps(self.data, indent=2, sort_keys=True)

    def update_status(self, message, status):
        self.status = status
        if status == 'BIBTEX':
            x = 8
        self.messages.append(message)

    @property
    def has_errors(self):
        return self.status == 'ERROR'


class BibtexImportResult():

    def __init__(self):
        self.result = []

    @property
    def has_errors(self):
        return len(self.errors()) > 0

    def errors(self):
        return [r for r in self.result if r.status == 'ERROR']

    def from_crossref(self):
        return [r for r in self.result if r.status == 'CROSSREF']

    def from_bibtex(self):
        return [r for r in self.result if r.status == 'BIBTEX']

    def skipped(self):
        return [r for r in self.result if r.status == 'SKIP']

    def counts(self):
        return dict(
            crossref=len(self.from_crossref()),
            bibtex=len(self.from_bibtex()),
            skipped=len(self.skipped()),
        )

    def append(self, entry):
        self.result.append(entry)


class BibtexResource():

    def __init__(self, bibtex_file, request, preserve_labels=True):
        self.model = get_work_model()
        self.result = BibtexImportResult()
        self.request = request
        self.preserve_labels = preserve_labels
        self.entries = self.parse_bibtex_file(bibtex_file)
        self.doi_list = (self.model.objects
                         .filter(DOI__isnull=False)
                         .values_list('DOI', flat=True)
                         )
        self.url_list = (self.model.objects
                         .filter(URL__isnull=False)
                         .values_list('URL', flat=True)
                         )

    def parse_bibtex_file(self, bibtex_file):
        """Parses an uploaded bibtex file.

        Args:
            bibtex_file: A Django file-like object

        Returns:
            list: A list of BibtexEntry objects
        """
        with TextIOWrapper(bibtex_file, encoding='utf-8') as f:
            parsed = bibtex.parse(f.read())
        return [BibtexEntry(entry) for entry in parsed]

    def fetch_from_crossref(self, entry):
        doi = entry.data.get('doi').lower()
        response = query_crossref_for_doi(doi, self.request)
        data = response['message']
        if self.preserve_labels:
            data['label'] = entry.data.get('label')
        return data

    def append_result(self, result_obj, code, message=None):
        result_obj.update_status(message, code)
        self.result.append(result_obj)

    def process(self):
        self.pbar = tqdm(total=len(self.entries))

        for entry in self.entries:
            if entry.data.get('doi'):
                if not self.doi_aleady_exists(entry):
                    try:  # to fetch data from the Crossref API
                        data = self.fetch_from_crossref(entry)
                    except HTTPError as e:
                        self.save_from_bibtex(entry)
                        # pass
                    else:
                        # Sometimes the returned DOI is slightly different from
                        # supplied DOI and is missed the first time
                        if not self.doi_aleady_exists(entry):
                            self.save_work_data_from_crossref(data, entry)
                        # else:
                        #     self.save_from_bibtex(entry)
            else:
                self.save_from_bibtex(entry)
            self.pbar.update(1)

    @transaction.atomic
    def save_work_data_from_crossref(self, data, entry):
        # use form to clean and validate crossref data
        form = CrossRefWorkForm(data)
        if form.is_valid():
            form.save()
            self.append_result(entry, code='CROSSREF')
        else:
            self.append_result(
                entry, code='ERROR', message=form.errors)
        self.pbar.update(1)

    @transaction.atomic
    def save_from_bibtex(self, entry):
        """Cleans and validates a bibtex entry using `BibtexForm`.

        Args:
            entry (dict): A BibtexEntry container
        """
        form = BibtexForm(entry.data)
        search_fields = ['label']

        # create a query to find any existing publications based on
        # search_fields
        query = Q()
        for field in search_fields:
            if entry.data.get(field):
                query.add(Q(**{field: entry.data.get(field)}), Q.OR)

        try:
            self.model.objects.filter(query).get()
        except (
                self.model.DoesNotExist,
                self.model.MultipleObjectsReturned):
            if form.is_valid():
                form.save()
                self.append_result(entry, code='BIBTEX')

            else:
                self.append_result(entry, code='ERROR', message=form.errors)

        self.pbar.update(1)

    def doi_aleady_exists(self, entry):
        """Checks if a given DOI already exists in the database

        Args:
            doi (str): DOI to be queried

        Throws:
            Works.DoesNotExist: raises if the DOI can't be found
        """
        doi = entry.data.get('doi').lower()
        if doi in self.doi_list:
            self.append_result(entry, code='SKIP')
            self.pbar.update(1)
            return True
