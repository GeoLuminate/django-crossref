from django.views.generic import ListView
from django.core.paginator import InvalidPage
from .paginators import YearPaginator
from .utils import get_work_model

Work = get_work_model()


class WorksByYearMixin(ListView):
    template_name = 'crossref/work_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.get_page(on='year', qs=context['filter'].qs)
        years = []
        if context['page']:
            for work in context['page'].object_list:
                if not years or (years[-1][0] != work.year):
                    years.append((work.year, []))
                years[-1][1].append(work)

        context['years'] = years
        return context

    def get_page(self, on, qs=None):
        if qs is None:
            paginator = YearPaginator(self.get_queryset(), on=on, per_page=self.paginate_by)
        else:
            paginator = YearPaginator(qs, on=on, per_page=self.paginate_by)

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            page = paginator.page(page)
        except (InvalidPage):
            page = paginator.page(paginator.num_pages)

        return page



class WorkList(WorksByYearMixin):
    model = Work
