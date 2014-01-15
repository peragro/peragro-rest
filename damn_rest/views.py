import os
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, link
from damn_rest.serializers import UserSerializer, GroupSerializer, FileDescriptionSerializer, FileDescriptionVerboseSerializer, AssetDescriptionSerializer


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


class FileDescriptionViewSet(viewsets.ViewSet):
    """
    List all snippets, or create a new snippet.
    """ 
    def list(self, request):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        references = []
        for filename in os.listdir(path):
            file_descr = store.get_metadata(path, filename)
            references.append(file_descr)

        serializer = FileDescriptionSerializer(references, many=True, exclude=('file.hash', 'assets', 'metadata'))
        return Response(serializer.data)

    #def create(self, request):
    #    pass
    
    @link(permission_classes=[])
    def full(self, request, pk=None):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        file_descr = store.get_metadata(path, pk)

        serializer = FileDescriptionVerboseSerializer(file_descr)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        file_descr = store.get_metadata(path, pk)

        serializer = FileDescriptionSerializer(file_descr)
        return Response(serializer.data)

    #def update(self, request, pk=None):
    #    pass

    #def partial_update(self, request, pk=None):
    #    pass

    #def destroy(self, request, pk=None):
    #    pass

from rest_framework.decorators import action

class AssetDescriptionViewSet(viewsets.ViewSet):
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
        file_descr = store.get_metadata(path, hash)
        
        for asset in file_descr.assets:
            if pk.startswith(asset.asset.subname):
                serializer = AssetDescriptionSerializer(asset)
        return Response(serializer.data)
