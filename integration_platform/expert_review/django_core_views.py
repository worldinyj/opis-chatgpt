"""Unexecuted Django connection adapter; synthetic only, disabled by default."""
from contextlib import closing
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import path
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .django_views import fixture_role
from .core_review import detail
from c09_connection import submit


@login_required
@csrf_protect
@require_http_methods(['GET','POST'])
def core_review(request,key):
    if not getattr(settings,'OPIS_SYNTHETIC_CORE_REVIEW_ENABLED',False):
        return HttpResponseForbidden('Synthetic core review disabled')
    try:
        role=fixture_role(request.user)
        factory=settings.OPIS_SYNTHETIC_CORE_CONNECTION_FACTORY
        with closing(factory()) as db:
            if request.method=='POST':
                submit(db,role,request.user.get_username(),int(request.POST.get('snapshot','')),key,request.POST.get('fingerprint',''),int(request.POST.get('revision','')),request.POST.get('decision',''),request.POST.get('reason',''))
                return redirect('opis_fixture_core_review',key=key)
            data=detail(db,role,key)
        return render(request,'opis_fixture/core_review.html',{'data':data})
    except PermissionError:
        return HttpResponseForbidden('Access denied')
    except (ValueError,KeyError,TypeError):
        return HttpResponse('Invalid request or changed snapshot. Reload before retrying.',status=409)


urlpatterns=[path('fixture/core-review/<str:key>/',core_review,name='opis_fixture_core_review')]
