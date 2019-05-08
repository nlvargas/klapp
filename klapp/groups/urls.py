from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^upload', views.upload_file, name='upload'),
    url(r'^download', views.download, name='download'),
    url(r'^$', views.index, name='index')
]