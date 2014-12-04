__author__ = 'ian'

from django.conf.urls import patterns, include, url
from script import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^scene/marriedtoolong', views.scene),
)