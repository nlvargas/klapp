from django.shortcuts import render
from .forms import UploadFileForm
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, Http404
from groups.groups_generator.heuristic import assign
import os


def download(request):
    path = "groups/groups_generator/results.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def index(request):
    context = {
        "title": 'App Grupos'}
    return render(request, "groups/index.html", context)


def upload(request):
    form = UploadFileForm()
    context = {
        "title": 'Subir Archivo',
        "form": form}
    return render(request, "groups/upload.html", context)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, 'Form submission successful')
            f = request.FILES['file']
            with open('groups/groups_generator/upload.xlsx', 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            assign()
            return render(request, 'groups/download.html', {'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'groups/upload.html', {'form': form})