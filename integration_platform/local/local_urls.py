from django.contrib.auth.views import LoginView
from django.urls import include,path
from django.views.generic import RedirectView
from expert_review.django_core_views import urlpatterns as review_patterns

urlpatterns=[path('',RedirectView.as_view(url='/fixture/core-review/SYNTHETIC-001-PA1/',permanent=False)),path('accounts/login/',LoginView.as_view(template_name='registration/login.html')),path('',include(review_patterns))]
