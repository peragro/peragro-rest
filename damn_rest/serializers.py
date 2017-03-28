from __future__ import absolute_import
from __future__ import print_function
import os
import urllib.request, urllib.parse, urllib.error

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
            print(('Exception', e))
            return ''


class MetaDataValueField(serializers.Field):
    def to_native(self, metadata):
        ret = {}
        if metadata:
            for key, value in list(metadata.items()):
                type_name = ['bool_value', 'int_value', 'double_value', 'string_value'][value.type-1]
                ret[key] = (MetaDataType._VALUES_TO_NAMES[value.type], getattr(value, type_name, None))
        return ret

from django_project.serializers import (
  HyperlinkedRelatedMethod,
  ExtendedHyperlinkedModelSerializer,
  GenericForeignKeyMixin
)

class BaseSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        self._exclude_fields = kwargs.get('exclude', [])
        if 'exclude' in kwargs:
            kwargs.pop('exclude')
        super(BaseSerializer, self).__init__(*args, **kwargs)
    def get_fields(self):
        fields = super(BaseSerializer, self).get_fields()
        for field in self._exclude_fields:
            fields.pop(field)
        return fields


class PathSerializer(GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    class Meta:
        from damn_rest.models import Path
        model = Path

    def to_native(self, path):
        ret = {}
        ret['id'] = path.pk
        ret['name'] = path.name
        ret['children'] = []
        for child in path.get_children():
            ret['children'].append(self.to_native(child))
        return ret


class FileReferenceSerializer(BaseSerializer, GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    uuid = serializers.CharField(source='hash')

    path = serializers.CharField(source='path.fullname')

    creator = HyperlinkedRelatedMethod()
    modifier = HyperlinkedRelatedMethod()
    date_created = serializers.DateField()
    date_modified = serializers.DateField()
    latest_version = serializers.IntegerField()
    nr_of_versions = serializers.IntegerField()

    class Meta:
        from damn_rest.models import FileReference
        model = FileReference
        exclude = ('_description', )


class AssetReferenceSerializer(BaseSerializer, GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    id = serializers.IntegerField()
    uuid = serializers.CharField(source='slug')
    url = serializers.HyperlinkedIdentityField(view_name='assetreference-detail', format='html')
    subname = serializers.CharField()
    mimetype = serializers.CharField()
    file = serializers.HyperlinkedRelatedField(view_name='filereference-detail', read_only=True)

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


class ObjectTaskSerializer(serializers.Serializer):
    def to_native(self, objecttask):
        #exclude = ('creator', 'modifier', 'date_created', 'date_modified', 'latest_version', 'nr_of_versions', )
        exclude = ()
        from damn_rest.models import FileReference, AssetReference
        #TODO: check objecttask type to determine serializer
        if isinstance(objecttask.content_object, AssetReference):
            data = AssetReferenceSerializer(objecttask.content_object, context=self.context, exclude=exclude).data
            data['type'] = 'assetreference'
            return data
        elif isinstance(objecttask.content_object, FileReference):
            data = FileReferenceSerializer(objecttask.content_object, context=self.context, exclude=exclude).data
            data['type'] = 'filereference'
            return data
        else:
            raise Exception()


class ReferenceTaskSerializer(GenericForeignKeyMixin, ExtendedHyperlinkedModelSerializer):
    references = ObjectTaskSerializer(source='objecttask_tasks', many=True)
    class Meta:
        from django_project.models import Task
        model = Task
        exclude = ['project', ]
