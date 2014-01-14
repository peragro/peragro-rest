import urllib
from django.contrib.auth.models import User, Group
from rest_framework import serializers

from damn_at import FileId, FileReference, AssetReference, MetaDataType



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
                print('recurse', object, field)
                path = field.split('.', 1)
                if len(path) == 1:
                    if path[0] in object.fields:
                        object.fields.pop(path[0])
                else:
                    recurse(object.fields[path[0]], path[1])
            
            for field in exclude:
                recurse(self, field)


class FileIdSerializer(DynamicFieldsSerializer):
    filename = serializers.CharField()
    hash = serializers.CharField(max_length=40)

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
        if isinstance(asset, AssetReference):
            asset = asset.asset
        return UniqueAssetId(asset)

class MetaDataValueField(serializers.RelatedField):
    def to_native(self, metadata):
        ret = {}
        for key, value in metadata.items():
            type_name = ['bool_value', 'int_value', 'double_value', 'string_value'][value.type-1]
            ret[key] = (MetaDataType._VALUES_TO_NAMES[value.type], getattr(value, type_name, None)) 
        return ret  
    
    
class AssetReferenceSerializer(DynamicFieldsSerializer):
    id = serializers.SerializerMethodField('get_id')
    asset = AssetIdSerializer()
    metadata = MetaDataValueField()
    #dependencies = AssetListingField(many=True)
    dependencies = AssetIdSerializer(many=True)
    
    def get_id(self, asset):
        return UniqueAssetId(asset.asset)

class FileReferenceSerializer(DynamicFieldsSerializer):
    id = serializers.CharField(source='file.hash')
    file = FileIdSerializer()
    #assets = AssetReferenceSerializer(many=True)
    assets = AssetListingField(many=True)

class FileReferenceVerboseSerializer(DynamicFieldsSerializer):
    id = serializers.CharField(source='file.hash')
    file = FileIdSerializer()
    assets = AssetReferenceSerializer(many=True, exclude=('metadata', 'dependencies'))
