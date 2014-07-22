from django.conf.urls import patterns, url, include
from rest_framework import routers
from damn_rest import views

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
#router.register(r'groups', views.GroupViewSet)

router.register(r'files', views.FileDescriptionViewSet, base_name = 'file')
router.register(r'assets', views.AssetDescriptionViewSet, base_name = 'assetreference')

import notifications
import django_project
from django_project.urls import router as routerp

#router.registry.extend(routerp.registry)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    
    url(r'^', include(django_project.urls)),
    
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^projects/(?P<project_name>\w+)/upload/', views.FileUploadView.as_view(), name='upload_file'),
    
    url(r'^admin/', include(admin.site.urls)),
)



urlpatterns += patterns('',
    ('^inbox/notifications/', include(notifications.urls)),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='toggle'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='follow'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='unfollow'),
)
