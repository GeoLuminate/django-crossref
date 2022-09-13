from crossref import views
from django.urls import path, include

app_name = 'crossref'
urlpatterns = [
    path('',views.publication_list, name='list'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]
