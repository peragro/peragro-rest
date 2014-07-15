# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AssetReference.slug'
        db.add_column(u'damn_rest_assetreference', 'slug',
                      self.gf('autoslug.fields.AutoSlugField')(default='', unique_with=(), max_length=50, populate_from=None),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AssetReference.slug'
        db.delete_column(u'damn_rest_assetreference', 'slug')


    models = {
        u'damn_rest.assetreference': {
            'Meta': {'unique_together': "(('file_id_hash', 'subname', 'mimetype'),)", 'object_name': 'AssetReference'},
            '_metadata': ('django.db.models.fields.TextField', [], {}),
            'file_id_filename': ('django.db.models.fields.TextField', [], {}),
            'file_id_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'}),
            'subname': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['damn_rest']