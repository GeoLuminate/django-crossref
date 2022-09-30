from crossref import views
from django.urls import path

app_name = 'crossref'
urlpatterns = [
    path('', views.WorkList.as_view(), name='work_list'),
]
