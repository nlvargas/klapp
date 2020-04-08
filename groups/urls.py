from django.conf.urls import url
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    url(r'^initial_form', views.initial_form, name='initial_form'),
    url(r'^input', views.input, name='input'),
    url(r'^create_groups', views.create_groups, name='create_groups'),
    url(r'^download_template', views.download_template, name='download_template'),
    url(r'^download', views.download, name='download'),
    url(r'^$', views.index, name='index')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)