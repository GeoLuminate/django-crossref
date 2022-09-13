from django.template import Library
from crossref.utils import get_publication_model
from django.template.loader import render_to_string
from django.conf import settings
from sekizai.context import SekizaiContext
from sekizai.helpers import get_varname

register = Library()

@register.inclusion_tag('crossref/publications.html', takes_context=True)
def get_publications(context, qs=None):
	"""Get all publications."""
	if not qs:
		qs = get_publication_model().objects.select_related()
	return {'publications': qs}

@register.inclusion_tag('crossref/publication.html', takes_context=True)
def get_publication(context, pub):
	""" Get a single publication."""
	return {'publication': pub}

@register.simple_tag(takes_context=True)
def bibliography(context, pub, style=None):
	"""Prints bibliography item in designated style"""
	if style is None:
		style = settings.CROSSREF_DEFAULT_STYLE
	return render_to_string(f"crossref/styles/{style}/bibliography.html", {'pub': pub})

@register.simple_tag(takes_context=True)
def cite(context, pub, cite_type='p', hyperlink=True, style=None):
	"""Prints citation item in designated style"""
	if style is None:
		style = settings.CROSSREF_DEFAULT_STYLE

	new_context = {
			'publications': pub,
			'type': cite_type,
			'hyperlink': hyperlink,
		}

	new_context[get_varname()] = context[get_varname()]
	return render_to_string(f"crossref/styles/{style}/cite.html", new_context)