import os
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action, link
from damn_rest.serializers import FileDescriptionSerializer, FileDescriptionVerboseSerializer, AssetDescriptionSerializer


from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import authentication, permissions

class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, project_name):
        print('FileUploadView', project_name)
        print('FileUploadView', request.FILES)
        file_obj = request.FILES['file']
        print(dir(file_obj))
        print(file_obj.name)
        print(file_obj.content_type)
        print(file_obj.read(8))
        # ...
        # do some staff with uploaded file
        # ...
        return Response(status=204)



class FileDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all snippets, or create a new snippet.
    """ 
    serializer_class = FileDescriptionSerializer
    paginate_by = 2
    
    def get_queryset(self):
        from damn_at import MetaDataStore
        path = '/tmp/damn'
        store = MetaDataStore(path)
        references = []
        for filename in os.listdir(path):
            file_descr = store.get_metadata(path, filename)
            references.append(file_descr)
        return references
        
    def get_object(self, queryset=None):
        pass
    
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


from rest_framework.decorators import action

class AssetDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all snippets, or create a new snippet.
    """ 
    serializer_class = AssetDescriptionSerializer
    
    def get_queryset(self):
        return []

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
