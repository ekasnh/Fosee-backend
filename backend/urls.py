from django.urls import path
from django.http import JsonResponse
def ok(r): return JsonResponse({"status":"backend-ready"})
urlpatterns=[path("",ok)]
