from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

import json
from django_project.managers import ObjectTaskMixin
from damn_at.utilities import get_metadatavalue_type, unique_asset_id_reference_from_fields

class AssetReferenceManager(models.Manager):
    def get_or_create(self, assetdescription):
      kwargs = {}
      kwargs['file_id_hash'] = assetdescription.asset.file.hash
      kwargs['subname'] = assetdescription.asset.subname
      kwargs['mimetype'] = assetdescription.asset.mimetype
      
      obj, created = super(AssetReferenceManager, self).get_or_create(**kwargs)
      if created:
        obj.file_id_filename = assetdescription.asset.file.filename
        metadata = {}
        if assetdescription.metadata:
            for name, value in assetdescription.metadata.items():
              metadata[name] = get_metadatavalue_type(value)
        obj.metadata = metadata
        obj.save()
      return obj, created


class AssetReference(ObjectTaskMixin):
    file_id_hash = models.CharField(max_length=128)
    file_id_filename = models.TextField()
    subname = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)
    _metadata = models.TextField()
    
    slug = models.TextField(db_index=True)
    
    objects = AssetReferenceManager()
    
    class Meta:
      unique_together = ('file_id_hash', 'subname', 'mimetype')
      
    def save(self, *args, **kwargs):
      self.slug = unique_asset_id_reference_from_fields(self.file_id_hash, self.subname, self.mimetype)
      super(AssetReference, self).save(*args, **kwargs)
    
    @property
    def metadata(self):
        if self._metadata:
            return json.loads(self._metadata)
        return {}
        
    @metadata.setter
    def metadata(self, data):
        self._metadata = json.dumps(data)

    def __unicode__(self):
        return 'AssetReference: %s %s (%s)'%(self.subname, self.mimetype, self.slug)
