from django.contrib import admin
from .mixins import WorkAdminMixin, AuthorAdminMixin, FunderAdminMixin
from ..models import Work, Author, Configuration, Subject
from solo.admin import SingletonModelAdmin


"""Default is to register all models in the Django Admin. If this behaviour
is not desired, these can be unregistered using `admin.site.deregister`
"""
admin.site.register(Configuration, SingletonModelAdmin)
admin.site.register(Work, WorkAdminMixin)
admin.site.register(Author, AuthorAdminMixin)
admin.site.register(Subject, admin.ModelAdmin)
