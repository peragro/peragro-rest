from django.conf.urls import patterns, url, include
from rest_framework import routers
from damn_rest import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

router.register(r'files', views.FileReferenceViewSet, base_name = 'files')
router.register(r'assets', views.AssetReferenceViewSet, base_name = 'assets')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token')
)
