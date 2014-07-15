# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AssetReference'
        db.create_table(u'damn_rest_assetreference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_id_hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('file_id_filename', self.gf('django.db.models.fields.TextField')()),
            ('subname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('_metadata', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'damn_rest', ['AssetReference'])

        # Adding unique constraint on 'AssetReference', fields ['file_id_hash', 'subname', 'mimetype']
        db.create_unique(u'damn_rest_assetreference', ['file_id_hash', 'subname', 'mimetype'])


    def backwards(self, orm):
        # Removing unique constraint on 'AssetReference', fields ['file_id_hash', 'subname', 'mimetype']
        db.delete_unique(u'damn_rest_assetreference', ['file_id_hash', 'subname', 'mimetype'])

        # Deleting model 'AssetReference'
        db.delete_table(u'damn_rest_assetreference')


    models = {
        u'damn_rest.assetreference': {
            'Meta': {'unique_together': "(('file_id_hash', 'subname', 'mimetype'),)", 'object_name': 'AssetReference'},
            '_metadata': ('django.db.models.fields.TextField', [], {}),
            'file_id_filename': ('django.db.models.fields.TextField', [], {}),
            'file_id_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subname': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['damn_rest']