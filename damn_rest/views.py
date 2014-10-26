import os
import tempfile

from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework_extensions.decorators import action, link
from rest_framework_extensions.mixins import NestedViewSetMixin

from damn_rest import serializers


from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import authentication, permissions

from django_project.views import FilteredModelViewSetMixin

from django_project.models import Project, Task
from damn_rest.models import Path, FileReference, AssetReference

from damn_at import Analyzer
from damn_at.utilities import calculate_hash_for_file

from damn_rest import filters as dp_filters

# curl -i -F filename=test2 -F file=@thumbs_up-600x600.png http://localhost:8000/projects/2/upload
class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    #authentication_classes = (authentication.TokenAuthentication,)
    #permission_classes = (permissions.IsAdminUser,)

    def post(self, request, project_name):
        project = get_object_or_404(Project, pk=project_name)


        if 'filename' not in request.POST or 'file' not in request.FILES:
            raise Response('Malformed request, needs to contain filename and file fields', status=400)

        path_id = request.POST['path_id']
        filename = os.path.basename(request.POST['filename'])
        file_obj = request.FILES['file']

        path = get_object_or_404(Path, pk=path_id)

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

            file_ref = FileReference.objects.update_or_create(request.user, project, path, filename, file_descr)

            return Response('FileReference with id %s created'%file_ref.id, status=204)




class PathViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = Path.objects.filter(parent=None)
    serializer_class = serializers.PathSerializer

    @link(is_for_list=True)
    def explore(self, request, **kwargs):
        project_id = kwargs['parent_lookup_project']
        path_id = request.QUERY_PARAMS.get('path_id', None)
        path_id = path_id if path_id and path_id.isdigit() else None
        def has_children(path):
            return path.get_children().count() > 0 or path.files.count() > 0
        def to_native(path):
            ret = {}
            ret['id'] = path.pk
            ret['text'] = path.name
            if has_children(path):
                ret['children'] = []
                for child in path.get_children():
                    ret['children'].append({'text': child.name,'id': child.pk, 'children': has_children(child)})
                for file in path.files.values('id', 'filename'):
                    ret['children'].append({'text': file['filename'], 'id': 'file_'+str(file['id']), 'icon': 'http://jstree.com/tree.png', 'type': 'file'})
            return ret
        filter = {'project': project_id}
        if path_id:
            filter['pk'] = path_id
        else:
            filter['parent'] = None
        return Response(to_native(Path.objects.get(**filter)))


class FileReferenceViewSet(NestedViewSetMixin, FilteredModelViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = FileReference.objects.all()
    slug_field = 'hash'

    filter_class = dp_filters.FileReferenceFilter
    search_fields = ('hash', )

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

    @link(is_for_list=True)
    def latest(self, request, **kwargs):
        ret = {}
        from reversion.models import Version
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(FileReference)
        latest = Version.objects.filter(content_type=content_type).latest('revision__date_created')
        return Response(serializers.FileReferenceVerboseSerializer(latest.object).data)


class AssetReferenceViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
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

        from damn_at.utilities import find_asset_id_in_file_descr

        file_descr = obj.file.description

        asset_id = find_asset_id_in_file_descr(file_descr, obj.subname, obj.mimetype)

        paths = transcode(file_descr, asset_id)
        print paths
        fsock = open(os.path.join('/tmp/damn/transcoded/', paths['256x256'][0]), 'rb')

        return StreamingHttpResponse(fsock, content_type='image/png')


class AssetRevisionsViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AssetReference.objects.all()

    def get_serializer_class(self):
      if 'pk' in self.kwargs:
          return serializers.AssetVersionVerboseSerializer
      return serializers.AssetVersionSerializer

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


class ReferenceTasksViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = Task.objects.exclude(objecttask_tasks=None)
    serializer_class = serializers.ReferenceTaskSerializer


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
