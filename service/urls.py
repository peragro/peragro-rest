from django.conf.urls import patterns, url, include
from damn_rest import views

from django.contrib import admin
admin.autodiscover()

from rest_framework_extensions.routers import ExtendedDefaultRouter

router = ExtendedDefaultRouter()

router.register(r'files', views.FileReferenceViewSet)
assets_router = router.register(r'assets', views.AssetReferenceViewSet)

assets_router.register(r'revisions', views.AssetRevisionsViewSet, base_name='assetreferences-revision', parents_query_lookups=['asset'])

import django_project
from django_project.urls import router as routerp

router.registry.extend(routerp.registry)

    
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

