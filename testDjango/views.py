from django.shortcuts import render, HttpResponse
from django.core.files.storage import default_storage
from service import detecService
from service import OCRService
import json


def hello(request):
    return render(request, 'index.html')


def run4det(request):
    try:
        file = request.FILES.get('uploadFile')
        name = default_storage.save(file.name, file)
        result = detecService.run(name, 0.5)
        default_storage.delete(name)
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
    except:
        result = {
            "flag": False
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


def run4ocr(request):
    try:
        file = request.FILES.get('uploadFile')
        name = default_storage.save(file.name, file)
        result = OCRService.run(name, 0.5)
        default_storage.delete(name)
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
    except:
        result = {
            "flag": False
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")