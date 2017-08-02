from django.conf.urls import include, url
from ballast import views

urlpatterns = [
    url(r'^$', views.show_Ballast, name='show_Ballast'),
]
