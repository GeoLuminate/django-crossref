"""Settings for Django CrossRef."""
from appconf import AppConf
from django.conf import settings

__all__ = ("settings", "CrossRefConf")

class CrossRefConf(AppConf):
    """Settings for Django CrossRef"""

    MODELS = {}
    """Point the application to the working models. Required when extending the default models."""


    DEFAULT_STYLE = 'harvard'
    """Default citation style. Must be included in the templates/crossref/styles folder."""


    AUTHOR_TRUNCATE_AFTER = 2


    BASE_URL = "https://api.crossref.org"


    API_KEY = None


    MAILTO = getattr(settings, 'DEFAULT_FROM_EMAIL')


    UA_STRING = None


    CMS_STYLES = [
                ('harvard', 'Harvard'),
            ]
    """Available styles for use in the Django CMS editing plugin."""

    class Meta:
        """Prefix for all Django CrossRef settings."""
        prefix = "CROSSREF"