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
                    recurse(object.fields[path[0]], path[1])
            
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
            
            
class FileIdSerializer(DynamicFieldsSerializer):
    filename = serializers.CharField()
    hash = serializers.CharField(max_length=40)
    base_name = serializers.SerializerMethodField('get_base_name')
    
    def get_base_name(self, file_id):
        return os.path.basename(file_id.filename)


class AssetIdSerializer(DynamicFieldsSerializer):
    subname = serializers.CharField()
    mimetype = serializers.CharField()
    file = FileIdSerializer()


class AssetListingField(UrlMixin, serializers.Serializer):
    view_name = 'assetreference-detail'
    
    id = serializers.SerializerMethodField('get_id')
    url = serializers.SerializerMethodField('get_url')
    
    def get_id(self, asset):
        return UniqueAssetId(asset.asset)


class MetaDataValueField(serializers.RelatedField):
    def to_native(self, metadata):
        ret = {}
        for key, value in metadata.items():
            type_name = ['bool_value', 'int_value', 'double_value', 'string_value'][value.type-1]
            ret[key] = (MetaDataType._VALUES_TO_NAMES[value.type], getattr(value, type_name, None)) 
        return ret  
    
    
class AssetDescriptionSerializer(UrlMixin, DynamicFieldsSerializer):
    view_name = 'assetreference-detail'
    
    id = serializers.SerializerMethodField('get_id')
    url = serializers.SerializerMethodField('get_url')
    asset = AssetIdSerializer()
    metadata = MetaDataValueField()
    #dependencies = AssetListingField(many=True)
    dependencies = AssetIdSerializer(many=True)
    
    def get_id(self, asset):
        return UniqueAssetId(asset.asset)


class FileDescriptionSerializer(UrlMixin, DynamicFieldsSerializer):
    view_name = 'file-detail'
    
    id = serializers.CharField(source='file.hash')
    url = serializers.SerializerMethodField('get_url')
    file = FileIdSerializer()
    mimetype = serializers.CharField()
    metadata = MetaDataValueField()
    assets = AssetListingField(many=True)

    def get_id(self, ref):
        return ref.file.hash


class FileDescriptionVerboseSerializer(FileDescriptionSerializer):
    assets = AssetDescriptionSerializer(many=True, exclude=('metadata', 'dependencies'))


class AssetReferenceSerializer(DynamicFieldsSerializer):
    id = serializers.IntegerField()
    uuid = serializers.CharField(source='slug')
    url = serializers.HyperlinkedIdentityField(view_name='assetreference-detail', format='html')
    def to_native(self, asset):
        ret = super(AssetReferenceSerializer, self).to_native(asset)
        ret['asset'] = {'mimetype': asset.mimetype, 'subname': asset.subname}
        ret['asset']['file'] = {'hash': asset.file_id_hash, 'filename': asset.file_id_filename}
        return ret


class AssetReferenceVerboseSerializer(DynamicFieldsSerializer):
    id = serializers.IntegerField()
    uuid = serializers.CharField(source='slug')
    url = serializers.HyperlinkedIdentityField(view_name='assetreference-detail', format='html')
    def to_native(self, asset):
        ret = super(AssetReferenceVerboseSerializer, self).to_native(asset)
        ret['asset'] = {'mimetype': asset.mimetype, 'subname': asset.subname}
        ret['asset']['file'] = {'hash': asset.file_id_hash, 'filename': asset.file_id_filename}
        ret['metadata'] = asset.metadata
        return ret        
