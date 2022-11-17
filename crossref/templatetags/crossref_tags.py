from calendar import c
from django.template import Library
from crossref.utils import get_work_model
from django.template.loader import render_to_string
from crossref.conf import settings
from sekizai.helpers import get_varname

Work = get_work_model()

register = Library()


@register.inclusion_tag('crossref/works.html', takes_context=True)
def get_works(context, qs=None):
    """Get all works."""
    if not qs:
        qs = Work.objects.select_related()
    return {'works': qs}


@register.inclusion_tag('crossref/work.html', takes_context=True)
def get_work(context, pub):
    """ Get a single work."""
    return {'work': pub}


@register.simple_tag(takes_context=True)
def bibliography(context, pub, style=None):
    """Prints bibliography item in designated style"""
    if style is None:
        style = settings.CROSSREF_DEFAULT_STYLE
    return render_to_string(
        f"crossref/styles/{style}/bibliography.html", {'pub': pub})


@register.simple_tag(takes_context=True)
def cite(context, work, style=None):
    """Prints citation item in designated style"""
    if style is None:
        style = settings.CROSSREF_DEFAULT_STYLE

    context.update({
        'works': work,
        'hyperlink': settings.CROSSREF_HYPERLINK,
    })

    # new_context[get_varname()] = context[get_varname()]
    return render_to_string(
        f"crossref/styles/{style}/in_text.html", context)


@register.simple_tag(takes_context=True)
def citep(context, work, style=None):
    """Prints citation item in designated style"""
    if style is None:
        style = settings.CROSSREF_DEFAULT_STYLE

    context.update({
        'works': work,
        'type': "p",
        'hyperlink': settings.CROSSREF_HYPERLINK,
    })

    return render_to_string(
        f"crossref/styles/{style}/in_text.html", context)
