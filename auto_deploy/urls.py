from django.conf.urls import url,include
from auto_deploy import views

urlpatterns = [
#    url(r'^$', views.login, name='login'),
    url(r'^index/$',views.index,name='index'),
    url(r'^index/env$',views.index_env,name='index_env'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^index/detail/$', views.index_detail, name='index_detail'),
    url(r'^index/getConsoleOutPut/$',views.get_console_output,name='console_output'),
    url(r'^index/startbuild/$', views.startbuild, name='start_build'),
    url(r'^index/startdeploy/$', views.startdeploy, name='start_deploy'),
    url(r'^index/uploadconfile/$', views.confile, name='confile'),
    url(r'^index/get_external_link/$',views.list_external_link,name='list_external_link'),
    url(r'^index/historylist/$', views.history_list, name='history_list'),
    url(r'^index/getexistexternallist/$', views.getexistexternallist, name='get_exist_external_list'),
    
    #    url(r'^logout/$', views.logout, name='logout'),
]
