import os
import urllib

from django.contrib.auth.models import User, Group
from rest_framework import serializers

from damn_at import FileId, FileDescription, AssetDescription, MetaDataType

from damn_at import utilities

def UniqueAssetId(asset_id):
    return utilities.unique_asset_id_reference(asset_id)


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

from django_project.serializers import (
  HyperlinkedRelatedMethod,
  ExtendedHyperlinkedModelSerializer,
  GenericForeignKeyMixin
)

class FileReferenceSerializer(GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    uuid = serializers.CharField(source='hash')
    base_name = serializers.SerializerMethodField('get_base_name')

    path = serializers.CharField(source='path.fullname')

    creator = HyperlinkedRelatedMethod()
    modifier = HyperlinkedRelatedMethod()
    date_created = serializers.DateField()
    date_modified = serializers.DateField()
    latest_version = serializers.IntegerField()
    nr_of_versions = serializers.IntegerField()

    def get_base_name(self, file_id):
        return os.path.basename(file_id.filename)

    class Meta:
        from damn_rest.models import FileReference
        model = FileReference
        exclude = ('_description', )


class AssetReferenceSerializer(GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    id = serializers.IntegerField()
    uuid = serializers.CharField(source='slug')
    url = serializers.HyperlinkedIdentityField(view_name='assetreference-detail', format='html')
    subname = serializers.CharField()
    mimetype = serializers.CharField()
    file = serializers.HyperlinkedRelatedField(view_name='filereference-detail')

    creator = HyperlinkedRelatedMethod()
    modifier = HyperlinkedRelatedMethod()
    date_created = serializers.DateField()
    date_modified = serializers.DateField()
    latest_version = serializers.IntegerField()
    nr_of_versions = serializers.IntegerField()

    class Meta:
        from damn_rest.models import AssetReference
        model = AssetReference
        exclude = ('_description',)


class FileReferenceVerboseSerializer(FileReferenceSerializer):
    assets = AssetReferenceSerializer(many=True)
    metadata = MetaDataValueField()


class AssetReferenceVerboseSerializer(AssetReferenceSerializer):
    file = FileReferenceSerializer()
    metadata = MetaDataValueField()


class AssetVersionSerializer(serializers.Serializer):
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
        exclude = ('date_modified', 'latest_version', 'nr_of_versions', )
        ver['asset'] = AssetReferenceVerboseSerializer(asset, context=self.context, exclude=exclude).data
        return ver
