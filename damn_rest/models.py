from collections import namedtuple

from django.db import models
from django.db.models import Q

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

from reversion import revisions as reversion
from django.db import transaction
class VersionMixin(object):
    def creator(self):
        version_list = reversion.get_for_object(self)
        return version_list.earliest('revision__date_created').revision.user

    def modifier(self):
        version_list = reversion.get_for_object(self)
        return version_list.latest('revision__date_created').revision.user

    def date_created(self):
        version_list = reversion.get_for_object(self)
        return version_list.earliest('revision__date_created').revision.date_created

    def date_modified(self):
        version_list = reversion.get_for_object(self)
        return version_list.latest('revision__date_created').revision.date_created

    def latest_version(self):
        version_list = reversion.get_for_object(self)
        return version_list.latest('revision__date_created').pk

    def versions(self):
        version_list = reversion.get_for_object(self)
        return version_list

    def nr_of_versions(self):
        version_list = reversion.get_for_object(self)
        return len(version_list)

    def save_revision(self, user, comment, *args, **kwargs):
        with transaction.atomic(), reversion.create_revision():
            self.save()
            if user.is_authenticated():
                reversion.set_user(user)
            reversion.set_comment(comment)


import json
from thrift.protocol.TJSONProtocol import TJSONProtocol
from damn_at.serialization import SerializeThriftMsg, DeserializeThriftMsg
from damn_at import AssetDescription, FileDescription
from damn_at.utilities import unique_asset_id_reference_from_fields

from django_project.managers import ObjectTaskMixin
from django_project.models import Project

class DescriptionModel(models.Model):
    _description = models.TextField()

    class Meta:
        abstract = True

    @property
    def description(self):
        if self._description:
            ret = DeserializeThriftMsg(self._description_model(), self._description, TJSONProtocol)
            return ret
        return None

    @description.setter
    def description(self, descr):
        self._description = SerializeThriftMsg(descr, TJSONProtocol)


from mptt.models import MPTTModel, TreeForeignKey

class PathManager(models.Manager):
    def get_or_create(self, project, path):
        with transaction.atomic():
            paths = path.split('/')
            paths.insert(0, '/')
            parent = None
            for p in paths:
                p = p.strip()
                if p != '':
                    obj, created = super(PathManager, self).get_or_create(project=project, parent=parent, name=p)
                    parent = obj

            return parent


class Path(MPTTModel):
    project = models.ForeignKey(Project, related_name='paths')
    name = models.TextField()
    fullname = models.TextField(editable=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    objects = PathManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return str(self.fullname)+', '+str(self.name)


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Path)
def path_pre_save_callback(sender, instance, *args, **kwargs):
    anc = instance.get_ancestors(include_self=True)
    instance.fullname = '/'.join([str(x.name) if x.name != '/' else '' for x in anc])


class FileReferenceManager(models.Manager):
    def update_or_create(self, user, project, path, filename, file_description):
        with transaction.atomic(), reversion.create_revision():
            try:
                fileref = FileReference.objects.get(project=project, path=path, filename=filename)
                created = False
            except FileReference.DoesNotExist:
                fileref = FileReference(project=project, path=path, filename=filename, hash='', mimetype='', _description='')
                created = True

            if not created and fileref.hash == file_description.file.hash:
                return fileref

            fileref.hash = file_description.file.hash
            fileref.mimetype = file_description.mimetype
            fileref.description = file_description
            #fileref.save_revision(user, 'Initial revision' if created else 'Updated file')
            fileref.save()

            assetids = []
            if file_description.assets:
                assetids = [(asset_description.asset.subname, asset_description.asset.mimetype) for asset_description in file_description.assets]
            # Delete assets that are not in the description
            qs = AssetReference.objects.filter(file=fileref)
            for assetref in qs:
                assetid = (assetref.subname, assetref.mimetype)
                if assetid not in assetids:
                    assetref.delete()

            # Update or create assets that are in the description
            if file_description.assets:
                for asset_description in file_description.assets:
                    AssetReference.objects.update_or_create(user, fileref, asset_description)

            if user.is_authenticated():
                reversion.set_user(user)
            reversion.set_comment('Initial revision' if created else 'Updated file')

            return fileref


class FileReference(VersionMixin, DescriptionModel):
    _description_model = FileDescription

    project = models.ForeignKey(Project, related_name='files')
    path = models.ForeignKey(Path, related_name='files')
    filename = models.TextField()
    hash = models.CharField(max_length=128, db_index=True)
    mimetype = models.CharField(max_length=255, null=True, blank=True)

    objects = FileReferenceManager()

    @property
    def metadata(self):
        return self.description.metadata

    def __unicode__(self):
        return 'FileReference: %s %s (%s)'%(self.filename, self.hash, self.mimetype)


class AssetReferenceManager(models.Manager):
    def update_or_create(self, user, fileref, asset_description):
        try:
            assetref = AssetReference.objects.get(file=fileref, subname=asset_description.asset.subname, mimetype=asset_description.asset.mimetype)
            created = False
        except AssetReference.DoesNotExist:
            assetref = AssetReference(file=fileref, subname=asset_description.asset.subname, mimetype=asset_description.asset.mimetype)
            created = True
        assetref.description = asset_description
        assetref.save()
        #assetref.save_revision(user, 'Initial revision' if created else 'Updated asset')
        return assetref


class AssetReference(VersionMixin, ObjectTaskMixin, DescriptionModel):
    _description_model = AssetDescription

    file = models.ForeignKey(FileReference, related_name='assets')
    subname = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255, null=True, blank=True)

    slug = models.TextField(db_index=True)

    objects = AssetReferenceManager()

    class Meta:
      unique_together = ('file', 'subname', 'mimetype')

    def save(self, *args, **kwargs):
      self.slug = unique_asset_id_reference_from_fields(self.file.hash, self.subname, self.mimetype)
      super(AssetReference, self).save(*args, **kwargs)

    @property
    def metadata(self):
        return self.description.metadata

    @property
    def dependencies(self):
        return self.description.dependencies

    def __unicode__(self):
        return 'AssetReference: %s %s (%s)'%(self.subname, self.mimetype, self.slug)


#reversion.register(FileReference, follow=["assets"])
reversion.register(FileReference)
reversion.register(AssetReference, follow=['file'])
