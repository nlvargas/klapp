from django.shortcuts import render
from .forms import TemplateInputForm, UploadTemplateForm, InputForm
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from groups.groups_generator.model import assign, assign_disponibility
from groups.groups_generator.params import create_template, clean_dict
from django.views.decorators.csrf import csrf_exempt
import os


def index(request):
    context = {
        "title": 'App Grupos'}
    return render(request, "groups/index.html", context)


@csrf_exempt
def initial_form(request):
    if request.method == 'POST':
        params = clean_dict(request.POST)
        if "divisions" not in params:
            params["divisions"] = []
        create_template(params)
        return HttpResponse()

    if request.method == 'GET':
        form = UploadTemplateForm()
        return render(request, "groups/initial_form.html", {'upload_form': form})


def download(request):
    path = "groups/groups_generator/results.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def download_template(request):
    path = "groups/groups_generator/template.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@csrf_exempt
def input(request):
    if request.method == "POST":
        form = UploadTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            with open('groups/groups_generator/input.xlsx', 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            return HttpResponse()
    raise Http404


@csrf_exempt
def create_groups(request):
    if request.method == 'POST':
        print(request.POST)
        params = clean_dict(request.POST)
        if not params["capacity"]:
            assign(params)
        else:
            assign_disponibility(params)
        return HttpResponse()
    raise Http404


