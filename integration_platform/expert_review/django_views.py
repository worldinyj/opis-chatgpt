"""Unexecuted Django adapter for isolated synthetic C06 service.
Host must configure OPIS_SYNTHETIC_REVIEW_CONNECTION_FACTORY and templates.
Do not deploy; actual authentication/CSRF/integration tests remain open.
"""
from contextlib import closing
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import path
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .c06_review import detail, submit


def fixture_role(user):
    if not user.is_authenticated or not user.is_active or not user.get_username().startswith('fixture:'):
        raise PermissionError('fixture accounts only')
    names=set(user.groups.filter(name__in=['EXPERT','QA','READER']).values_list('name',flat=True))
    if len(names)!=1:
        raise PermissionError('one explicit fixture role required')
    return names.pop()


@login_required
@csrf_protect
@require_http_methods(['GET','POST'])
def review(request,key):
    try:
        role=fixture_role(request.user)
        factory=settings.OPIS_SYNTHETIC_REVIEW_CONNECTION_FACTORY
        with closing(factory()) as db:
            if request.method=='POST':
                submit(db,role,request.user.get_username(),key,request.POST.get('fingerprint',''),
                       int(request.POST.get('revision','')),request.POST.get('decision',''),request.POST.get('reason',''))
                return redirect('opis_fixture_review',key=key)
            data=detail(db,role,key)
        return render(request,'opis_fixture/review.html',{'data':data,'can_edit':role=='EXPERT' and data['status']!='PENDING_INPUT'})
    except PermissionError:
        return HttpResponseForbidden('Access denied')
    except ValueError:
        return HttpResponse('Invalid request or changed snapshot/revision. Reload before retrying.',status=409)


urlpatterns=[path('fixture/review/<str:key>/',review,name='opis_fixture_review')]
