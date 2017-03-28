from __future__ import absolute_import
from django.conf.urls import patterns, url, include
from damn_rest import views

from django.contrib import admin
admin.autodiscover()

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_extensions.routers import ExtendedDefaultRouter

router = ExtendedDefaultRouter()

# Path router
paths_router = router.register(r'paths', views.PathViewSet)

# File router and its nested routes
files_router = router.register(r'files', views.FileReferenceViewSet)
files_router.register(r'assets', views.AssetReferenceViewSet, base_name='files-asset', parents_query_lookups=['file'])

# Asset router and its nested routes
assets_router = router.register(r'assets', views.AssetReferenceViewSet)
assets_router.register(r'revisions', views.AssetRevisionsViewSet, base_name='assetreferences-revision', parents_query_lookups=['asset'])

# ReferenceTask router
router.register(r'referencetasks', views.ReferenceTasksViewSet, base_name='referencetasks')

import django_project
from django_project.urls import router as routerp
from django_project.urls import projects_router

# Project router and its nested routes
projects_router.register(r'files', views.FileReferenceViewSet, base_name='projects-filereference', parents_query_lookups=['project'])
projects_router.register(r'assets', views.AssetReferenceViewSet, base_name='projects-assetreference', parents_query_lookups=['file__project'])
projects_router.register(r'paths', views.PathViewSet, base_name='projects-path', parents_query_lookups=['project'])

# Extend our registery with the django_project registery
router.registry.extend(routerp.registry)

#curl -X POST -d "username=admin&password=admin" http://localhost:8000/api-token-auth/
urlpatterns = [
    url(r'^', include(router.urls)),

    url(r'^', include(django_project.urls)),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token),

    url(r'^projects/(?P<project_name>\w+)/upload/', views.FileUploadView.as_view(), name='upload_file'),

    url(r'^admin/', include(admin.site.urls)),
]
