from django.contrib import admin
from django.utils.translation import gettext as _


class HasORCID(admin.SimpleListFilter):

    title = _('has ORCID')
    parameter_name = 'has_orcid'

    def lookups(self, request, model_admin):

        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'yes':
            return queryset.filter(ORCID__isnull=False)

        if self.value() == 'no':
            return queryset.filter(ORCID__isnull=True)


class AuthorType(admin.SimpleListFilter):

    title = _('author type')
    parameter_name = 'author_type'

    def lookups(self, request, model_admin):

        return (
            ('as_lead', _('Lead')),
            ('as_supporting', _('Supporting')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'as_lead':
            return queryset.filter(as_lead__gt=0)

        if self.value() == 'as_supporting':
            return queryset.filter(as_lead=0)
