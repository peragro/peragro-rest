import os
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, link
from damn_rest.serializers import UserSerializer, GroupSerializer, FileReferenceSerializer, FileReferenceVerboseSerializer, AssetReferenceSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FileReferenceViewSet(viewsets.ViewSet):
    """
    List all snippets, or create a new snippet.
    """ 
    def list(self, request):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        references = []
        for filename in os.listdir(path):
            a_file_reference = store.get_metadata(path, '90ca0b2230d6f9b486cd932e1ae1c28b780a2b0c')
            references.append(a_file_reference)

        serializer = FileReferenceSerializer(references, many=True, exclude=('file.hash', 'assets'))
        return Response(serializer.data)

    #def create(self, request):
    #    pass
    
    @link(permission_classes=[])
    def full(self, request, pk=None):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        a_file_reference = store.get_metadata(path, pk)

        serializer = FileReferenceVerboseSerializer(a_file_reference)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        a_file_reference = store.get_metadata(path, pk)

        serializer = FileReferenceSerializer(a_file_reference)
        return Response(serializer.data)

    #def update(self, request, pk=None):
    #    pass

    #def partial_update(self, request, pk=None):
    #    pass

    #def destroy(self, request, pk=None):
    #    pass

from rest_framework.decorators import action

class AssetReferenceViewSet(viewsets.ViewSet):
    """
    List all snippets, or create a new snippet.
    """ 
    
    @action(permission_classes=[])
    def set_password(self, request, pk=None):
        pass

    def retrieve(self, request, pk=None):
        hash = pk[:40]
        pk = pk[40:]
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        a_file_reference = store.get_metadata(path, hash)
        
        for asset in a_file_reference.assets:
            if pk.startswith(asset.asset.subname):
                serializer = AssetReferenceSerializer(asset)
        return Response(serializer.data)
