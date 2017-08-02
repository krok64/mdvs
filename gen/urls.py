from django.conf.urls import include, url

from gen import views, genvr
from gen.views import ZavodListView, ZavodCreate, ZavodUpdate, ZavodDelete

urlpatterns = [
    url(r'^$' , views.show_Proj, name='show_Proj'),
    url(r'^delete/(?P<id>\d+)/$', views.show_Proj, name='show_Proj'),
    url(r'^edit/(?P<id>\d+)/$', views.show_ProjEd, name='show_ProjEd'),
    url(r'^copy/(?P<s_id>\d+)/$', views.show_CopySpecForm, name='show_CopySpecForm'),
    url(r'^select/(?P<id>\d+)/$', views.show_ProjItems, name='show_ProjItems'),
    url(r'^zavod/$', ZavodListView.as_view(), name='zavod'),
    url(r'^zavod/create/$', ZavodCreate.as_view(), name='zavodcreate'),
    url(r'^zavod/(?P<id>\d+)/ed/$', ZavodUpdate.as_view(), name='zavodupdate'),
    url(r'^zavod/(?P<id>\d+)/del/$', ZavodDelete.as_view(), name='zavoddelete'),
    url(r'^type/$', views.show_Type, name='show_Type'),
    url(r'^type/(?P<id>\d+)/$', views.show_Type, name='show_Type'),
    url(r'^type/(?P<id>\d+)/ed/$', views.show_TypeEd, name='show_TypeEd'),
    url(r'^tu/$', views.show_TU, name='show_TU'),
    url(r'^tu/(?P<id>\d+)/$', views.show_TU, name='show_TU'),
    url(r'^tu/(?P<id>\d+)/ed/$', views.show_TUEd, name='show_TUEd'),
    url(r'^item/$', views.show_Item, name='show_Item'),
    url(r'^item/(?P<id>\d+)/$', views.show_Item, name='show_Item'),
    url(r'^item/(?P<id>\d+)/copy/$', views.copyItem, name='copyItem'),
    url(r'^item/(?P<id>\d+)/ed/$', views.show_ItemEd, name='show_ItemEd'),
    url(r'^item/(?P<id>\d+)/ed/(?P<s_id>\d+)$', views.show_ItemEd, name='show_ItemEd'),
    url(r'^sql/$', views.show_SQL, name='show_SQL'),
    url(r'^select/(?P<s_id>\d+)/(?P<d_id>\d+)/', views.show_AddItemForm, name='show_AddItemForm'),
    url(r'^select/(?P<s_id>\d+)/del/(?P<l_id>\d+)/', views.DelItem, name='DelItem'),
    url(r'^select/(?P<s_id>\d+)/chg/(?P<l_id>\d+)/', views.ChangeNumItems, name='ChangeNumItems'),
    url(r'^select/(?P<s_id>\d+)/f1/(?P<t_id>\d+)/', views.ItemsFilterType, name='ItemsFilterType'),
    url(r'^select/(?P<s_id>\d+)/f2/(?P<dy_id>\d+)/', views.ItemsFilterDY, name='ItemsFilterDY'),
]

urlpatterns += [
    url(r'^genvr/(?P<spec_id>\d+)/$', genvr.gen_VR, name='gen_VR'),
    url(r'^genso/(?P<spec_id>\d+)/$', genvr.gen_SO, name='gen_SO'),
]
