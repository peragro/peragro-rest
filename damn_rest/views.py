import os
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action, link
from damn_rest.serializers import FileDescriptionSerializer, FileDescriptionVerboseSerializer, AssetReferenceSerializer, AssetReferenceVerboseSerializer


from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import authentication, permissions

from damn_rest.models import AssetReference

class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    
    #authentication_classes = (authentication.TokenAuthentication,)
    #permission_classes = (permissions.IsAdminUser,)

    def post(self, request, project_name):
        print('FileUploadView', project_name)
        print('FileUploadView', request.FILES)
        file_obj = request.FILES['file']
        print(dir(file_obj))
        print(file_obj.name)
        print(file_obj.content_type)
        # ...
        # do some staff with uploaded file
        # ...
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as destination:
          print destination.name
          for chunk in file_obj.chunks():
              destination.write(chunk)
          destination.flush()    
          from damn_at import mimetypes
          print mimetypes.guess_type(destination.name, False)
          
          import logging
          from damn_at import MetaDataStore, Analyzer
          from damn_at.analyzer import analyze
          logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
          
          analyzer = Analyzer()
          metadatastore = MetaDataStore('/tmp/damn')  
          output = logging.getLogger('damn-at_analyzer')
          
          descr = analyze(analyzer, metadatastore, destination.name, output, forcereanalyze=True)
          print descr
          for asset in descr.assets:
            ref = AssetReference.objects.get_or_create(asset)
        return Response(status=204)



class FileDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
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


from django.shortcuts import get_object_or_404
from django.http import HttpResponse

class AssetDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """ 
    
    def get_serializer_class(self):
      if 'pk' in self.kwargs:
          return AssetReferenceVerboseSerializer
      return AssetReferenceSerializer
    
    def get_queryset(self):
        return AssetReference.objects.all()
        
    def get_object(self):
        queryset = self.get_queryset()
        filter = {'pk': self.kwargs['pk']}

        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj
    
    @link(permission_classes=[])
    def tasks(self, request, pk):
        obj = self.get_object()
        
        from django_project.serializers import TaskSerializer
        serializer = TaskSerializer(obj.tasks, many=True)
        
        return Response(serializer.data)
        
    @link(permission_classes=[])
    def preview(self, request, pk):
        queryset = self.get_queryset()
        filter = {'pk': self.kwargs['pk']}

        obj = get_object_or_404(queryset, **filter)
        
        
        from damn_at import MetaDataStore
        from damn_at.utilities import find_asset_id_in_file_descr
        path = '/tmp/damn'
        store = MetaDataStore(path)
        file_descr = store.get_metadata(path, obj.file_id_hash)
        
        asset_id = find_asset_id_in_file_descr(file_descr, obj.subname, obj.mimetype)
        
        paths = transcode(file_descr, asset_id)
        print paths
        fsock = open(os.path.join('/tmp/transcoded/', paths['256x256'][0]), 'rb')

        return HttpResponse(fsock, mimetype='image/png')



def transcode(file_descr, asset_id, dst_mimetype='image/png', options={}, path='/tmp/transcoded/'):
    """
    Transcode the given asset_id to the destination mimetype
    and return the paths to the transcoded files.
    """
    from damn_at import Transcoder
    t = Transcoder(path)    
    
    preview_paths = {}
    
    
    target_mimetype = t.get_target_mimetype(asset_id.mimetype, dst_mimetype)
    if target_mimetype:
        for size in ['256,256']:
            options = t.parse_options(asset_id.mimetype, target_mimetype, size=size, angles='0')
            
            paths = t.get_paths(asset_id, target_mimetype, **options)    
            exists = all(map(lambda x: os.path.exists(os.path.join(path, x)), paths))
            print paths, exists
            if not exists:
                print('Transcoding', asset_id.subname, file_descr.file.filename)
                t.transcode(file_descr, asset_id, dst_mimetype, **options)
            #print('get_paths', asset_id.mimetype, paths)
            preview_paths[size.replace(',', 'x')] = paths
            preview_paths['exists-'+size.replace(',', 'x')] = map(lambda x: os.path.exists(os.path.join(path, x)), paths)
    else:
        #print(t.get_target_mimetypes().keys())
        print('get_paths FAILED', asset_id.mimetype, dst_mimetype)
        raise Exception('No such transcoder %s - %s'%(asset_id.mimetype, dst_mimetype))
         
    return preview_paths
