from crossref import views
from django.urls import path

app_name = 'crossref'
urlpatterns = [
    path('', views.WorkList.as_view(), name='work_list'),
    # path('<pk>/', views.WorkDetail.as_view(), name='work_detail'),
    # path('authors/', views.AuthorList.as_view(), name='author_list'),
    # path('authors/<pk>/', views.AuthorDetail.as_view(), name='author_detail'),
]
