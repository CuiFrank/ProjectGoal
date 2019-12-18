

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'goal/', views.set_goal),
    url(r'rank/', views.get_rank)
]
