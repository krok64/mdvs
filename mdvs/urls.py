from django.conf.urls import include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from gost24950 import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico'), name='favicon'),
    url(r'^gost24950/$', views.show_gost24950, name='show_gost24950'),
    url(r'^vgidro/$', views.show_VGidro, name='show_VGidro'),
    url(r'^massatr/$', views.show_MassaTr, name='show_MassaTr'),
    url(r'^vimpuls/$', views.show_VImpuls, name='show_VImpuls'),
    url(r'^vsgaza/$', views.show_VSGaza, name='show_VSGaza'),
    url(r'^transh/$', views.show_Transh, name='show_Transh'),
    url(r'^srezka/$', views.show_Srezka, name='show_Srezka'),
    url(r'^kotlovan/$', views.show_Kotlovan, name='show_Kotlovan'),
    url(r'^vkotlovan/$', views.show_VKotlovan, name='show_VKotlovan'),
    url(r'^valik/$', views.show_Valik, name='show_Valik'),
    url(r'^sovug/$', views.show_SovUg, name='show_SovUg'),
    url(r'^progal/$', views.show_Progal, name='show_Progal'),
    url(r'^gaztu/$', views.show_GazTU, name='show_GazTU'),
    url(r'^pipe/$', views.show_Pipe, name='show_Pipe'),
    url(r'^kojux/$', views.show_Kojux, name='show_Kojux'),
    url(r'^pipe/delete/(?P<id>\d+)/$', views.show_Pipe, name='show_Pipe'),
    url(r'^pipe/select/(?P<pipe_id>\d+)/$', views.show_PipeObj, name='show_PipeObj'),
    url(r'^pipe/obj/(?P<pipe_id>\d+)/(?P<action>del)/(?P<obj_id>\d+)/$', views.show_PipeObj, name='show_PipeObj'),
    url(r'^pipe/obj/(?P<pipe_id>\d+)/(?P<action>ed)/(?P<obj_id>\d+)/$', views.show_PipeObjEd, name='show_PipeObjEd'),
    url(r'^proj/', include('gen.urls')),
    url(r'^ballast/', include('ballast.urls')),
    # Examples:
    # url(r'^$', 'mdvs.views.home', name='home'),
    # url(r'^mdvs/', include('mdvs.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
