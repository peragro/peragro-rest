import os
import tempfile

from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action, link
from rest_framework_extensions.mixins import NestedViewSetMixin

from damn_rest import serializers


from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import authentication, permissions

from django_project.models import Project
from damn_rest.models import FileReference, AssetReference

from damn_at import Analyzer
from damn_at.utilities import calculate_hash_for_file

# curl -i -F filename=test2 -F file=@thumbs_up-600x600.png http://localhost:8000/projects/2/upload
class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    
    #authentication_classes = (authentication.TokenAuthentication,)
    #permission_classes = (permissions.IsAdminUser,)

    def post(self, request, project_name):
        project = get_object_or_404(Project, pk=project_name)
        
        if 'filename' not in request.POST or 'file' not in request.FILES:
            raise Response('Malformed request, needs to contain filename and file fields', status=400)
        
        filename = request.POST['filename']   
        file_obj = request.FILES['file']
         
        #Write file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
            destination.flush() 

            hash = calculate_hash_for_file(destination.name)

            files_dir = '/tmp/damn/files'
            if not os.path.exists(files_dir):
                os.makedirs(files_dir) 
            new_path = os.path.join(files_dir, hash)
            os.rename(destination.name, new_path)

            analyzer = Analyzer()
            file_descr = analyzer.analyze_file(new_path)
            file_descr.file.hash = hash

            file_ref = FileReference.objects.update_or_create(request.user, project, filename, file_descr)

            return Response('FileReference with id %s created'%file_ref.id, status=204)


class FileReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """ 
    queryset = FileReference.objects.all()
    slug_field = 'hash'
    
    def get_serializer_class(self):
      if 'pk' in self.kwargs:
          return serializers.FileReferenceVerboseSerializer
      return serializers.FileReferenceSerializer
    
    @link(permission_classes=[])
    def download(self, request, pk=None):
        obj = self.get_object()
        
        hash = obj.hash
        path = '/tmp/damn/files'
        fsock = open(os.path.join(path, hash), 'rb')
        return StreamingHttpResponse(fsock, content_type=file_descr.mimetype)


class AssetReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """ 
    queryset = AssetReference.objects.all()
    slug_field = 'slug'
    
    def get_serializer_class(self):
      if 'pk' in self.kwargs:
          return serializers.AssetReferenceVerboseSerializer
      return serializers.AssetReferenceSerializer
    
    @link(permission_classes=[])
    def tasks(self, request, pk):
        obj = self.get_object()
        
        from django_project.serializers import TaskSerializer
        serializer = TaskSerializer(obj.tasks, many=True)
        
        return Response(serializer.data)
        
    @link(permission_classes=[])
    def preview(self, request, pk):
        obj = self.get_object()
        
        
        from damn_at import MetaDataStore
        from damn_at.utilities import find_asset_id_in_file_descr
        path = '/tmp/damn'
        store = MetaDataStore(path)
        file_descr = store.get_metadata(path, obj.file_id_hash)
        
        asset_id = find_asset_id_in_file_descr(file_descr, obj.subname, obj.mimetype)
        
        paths = transcode(file_descr, asset_id)
        print paths
        fsock = open(os.path.join('/tmp/transcoded/', paths['256x256'][0]), 'rb')

        return StreamingHttpResponse(fsock, content_type='image/png')


class AssetRevisionsViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    from django_project import serializers as dp_serializers
    serializer_class = dp_serializers.VersionSerializer
    queryset = AssetReference.objects.all()
    def get_queryset(self):
        qs = super(AssetRevisionsViewSet, self).get_queryset()[0].versions() 
        return qs
    def get_parents_query_dict(self):
        filters = {}
        from rest_framework_extensions.settings import extensions_api_settings
        for kwarg_name in self.kwargs:
            if kwarg_name.startswith(extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX):
                if self.kwargs[kwarg_name].isnumeric():
                    filter = {'id': self.kwargs[kwarg_name]}
                else:
                    filter = {'slug': self.kwargs[kwarg_name]}
                filters.update(filter)
        return filters
        
    @link(permission_classes=[])
    def preview(self, request, parent_lookup_asset, pk):
        version = self.get_queryset().get(pk=pk)

        from damn_at.utilities import find_asset_id_in_file_descr
        asset = version.object_version.object
        
        #Why doesn't it restore the related fields?
        #file = asset.file
        #file_descr = file.description
        # Begin work-around
        file_version = version.revision.version_set.exclude(pk=version.pk).all()[0]
        file = file_version.object_version.object
        file_descr = file.description
        # End work-around
        
        file_descr.file.filename = os.path.join('/tmp/damn/files', file.hash)
        
        asset_id = find_asset_id_in_file_descr(file_descr, asset.subname, asset.mimetype)
        
        paths = transcode(file_descr, asset_id)
        fsock = open(os.path.join('/tmp/damn/transcoded/', paths['256x256'][0]), 'rb')

        return StreamingHttpResponse(fsock, content_type='image/png')
        

def transcode(file_descr, asset_id, dst_mimetype='image/png', options={}, path='/tmp/damn/transcoded/'):
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
