import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers

from damn_at import FileId, FileDescription, AssetDescription, MetaDataType



def UniqueAssetId(asset_id):
    name = '%s%s%s' % (asset_id.file.hash, asset_id.subname, asset_id.mimetype)
    return urllib.quote(name.replace('/', '|'))


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
        
        
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


class FileIdSerializer(DynamicFieldsSerializer):
    filename = serializers.CharField()
    hash = serializers.CharField(max_length=40)
    base_name = serializers.SerializerMethodField('get_base_name')
    
    def get_base_name(self, file_id):
        return os.path.basename(file_id.filename)

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.email = attrs.get('email', instance.email)
            instance.content = attrs.get('content', instance.content)
            instance.created = attrs.get('created', instance.created)
            return instance
        return Comment(**attrs)


class AssetIdSerializer(DynamicFieldsSerializer):
    subname = serializers.CharField()
    mimetype = serializers.CharField()
    file = FileIdSerializer()

class AssetListingField(serializers.RelatedField):
    def to_native(self, asset):
        if isinstance(asset, AssetDescription):
            asset = asset.asset
        return UniqueAssetId(asset)

class MetaDataValueField(serializers.RelatedField):
    def to_native(self, metadata):
        ret = {}
        for key, value in metadata.items():
            type_name = ['bool_value', 'int_value', 'double_value', 'string_value'][value.type-1]
            ret[key] = (MetaDataType._VALUES_TO_NAMES[value.type], getattr(value, type_name, None)) 
        return ret  
    
    
class AssetDescriptionSerializer(DynamicFieldsSerializer):
    id = serializers.SerializerMethodField('get_id')
    asset = AssetIdSerializer()
    metadata = MetaDataValueField()
    #dependencies = AssetListingField(many=True)
    dependencies = AssetIdSerializer(many=True)
    
    def get_id(self, asset):
        return UniqueAssetId(asset.asset)

class FileDescriptionSerializer(DynamicFieldsSerializer):
    id = serializers.CharField(source='file.hash')
    file = FileIdSerializer()
    metadata = MetaDataValueField()
    #assets = AssetDescriptionSerializer(many=True)
    assets = AssetListingField(many=True)

class FileDescriptionVerboseSerializer(DynamicFieldsSerializer):
    id = serializers.CharField(source='file.hash')
    file = FileIdSerializer()
    metadata = MetaDataValueField()
    assets = AssetDescriptionSerializer(many=True, exclude=('metadata', 'dependencies'))
