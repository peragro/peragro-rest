import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers

from damn_at import FileId, FileDescription, AssetDescription, MetaDataType

from damn_at import utilities

def UniqueAssetId(asset_id):
    return utilities.unique_asset_id_reference(asset_id)


class DynamicFieldsSerializer(serializers.Serializer):        
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        exclude = kwargs.pop('exclude', None)
        
        # Instantiate the superclass normally
        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)

        if exclude:      
            # Drop any fields that are not specified in the `fields` argument.
            def recurse(object, field):
                path = field.split('.', 1)
                if len(path) == 1:
                    if path[0] in object.fields:
                        if not hasattr(object, '_DynamicFieldsSerializer__excluded_fields'):
                            object.__excluded_fields = []
                        object.__excluded_fields.append(path[0])
                else:
                    if path[0] in object.fields:
                        recurse(object.fields[path[0]], path[1])
                    else:
                        if not hasattr(object, '_DynamicFieldsSerializer__excluded_fields'):
                            object.__excluded_fields = []
                        object.__excluded_fields.append(path[0])
            
            for field in exclude:
                recurse(self, field)
                
    def to_native(self, obj):
        ret = super(DynamicFieldsSerializer, self).to_native(obj)
        fields = getattr(self, '_DynamicFieldsSerializer__excluded_fields', [])
        for field in fields:
            if field in ret:
                del ret[field]
        return ret


class UrlMixin:
    def get_url(self, obj):
        try:
            from rest_framework.reverse import reverse
            kwargs = {'pk': self.get_id(obj)}
            return reverse(self.view_name, kwargs=kwargs, request=self.context.get('request', None), format=None)
        except Exception as e:
            print('Exception', e)
            return ''
            

class MetaDataValueField(serializers.RelatedField):
    def to_native(self, metadata):
        ret = {}
        for key, value in metadata.items():
            type_name = ['bool_value', 'int_value', 'double_value', 'string_value'][value.type-1]
            ret[key] = (MetaDataType._VALUES_TO_NAMES[value.type], getattr(value, type_name, None)) 
        return ret  

from django_project.serializers import ExtendedHyperlinkedModelSerializer

class FileReferenceSerializer(ExtendedHyperlinkedModelSerializer):
    uuid = serializers.CharField(source='hash')
    base_name = serializers.SerializerMethodField('get_base_name')
    
    def get_base_name(self, file_id):
        return os.path.basename(file_id.filename)
        
    class Meta:
        from damn_rest.models import FileReference
        model = FileReference
        exclude = ('_description', )


class AssetReferenceSerializer(DynamicFieldsSerializer):
    id = serializers.IntegerField()
    uuid = serializers.CharField(source='slug')
    url = serializers.HyperlinkedIdentityField(view_name='assetreference-detail', format='html')
    subname = serializers.CharField()
    mimetype = serializers.CharField()
    file = FileReferenceSerializer()
    date_created = serializers.DateField()
    latest_version = serializers.IntegerField()
    nr_of_versions = serializers.IntegerField()


class FileReferenceVerboseSerializer(FileReferenceSerializer):
    assets = AssetReferenceSerializer(many=True, exclude=('file',))
    metadata = MetaDataValueField()


class AssetReferenceVerboseSerializer(AssetReferenceSerializer):
    metadata = MetaDataValueField()


class AssetVersionSerializer(DynamicFieldsSerializer):  
    id = serializers.IntegerField()
    def to_native(self, version):
        ver = super(AssetVersionSerializer, self).to_native(version)
        from rest_framework.reverse import reverse
        kwargs = {'pk': version.pk, 'parent_lookup_asset': version.object_id}
        ver['url'] = reverse('assetreferences-revision-detail', kwargs=kwargs, request=self.context.get('request', None), format=None)
        
        ver['revision'] = {}
        #ver['revision']['id'] = version.revision_id
        ver['revision']['comment'] = version.revision.comment
        if version.revision.user:
            ver['revision']['editor'] = version.revision.user.username
        else:
            ver['revision']['editor'] = 'Anonymous'
        ver['revision']['date_created'] = version.revision.date_created
        return ver


class AssetVersionVerboseSerializer(AssetVersionSerializer):   
    def to_native(self, version):
        ver = super(AssetVersionVerboseSerializer, self).to_native(version)
        
        asset = version.object_version.object
        #Why doesn't it restore the related fields?
        # Begin work-around
        file_version = version.revision.version_set.exclude(pk=version.pk).all()[0]
        asset.file = file_version.object_version.object
        # End work-around
        exclude = ('date_created', 'latest_version', 'nr_of_versions', )
        ver['asset'] = AssetReferenceVerboseSerializer(asset, context=self.context, exclude=exclude).data
        return ver
