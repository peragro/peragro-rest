# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileReference'
        db.create_table(u'damn_rest_filereference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('_metadata', self.gf('django.db.models.fields.TextField')()),
            ('_file_description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'damn_rest', ['FileReference'])


        # Changing field 'AssetReference.slug'
        db.alter_column(u'damn_rest_assetreference', 'slug', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):
        # Deleting model 'FileReference'
        db.delete_table(u'damn_rest_filereference')


        # Changing field 'AssetReference.slug'
        db.alter_column(u'damn_rest_assetreference', 'slug', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), populate_from=None))

    models = {
        u'damn_rest.assetreference': {
            'Meta': {'unique_together': "(('file_id_hash', 'subname', 'mimetype'),)", 'object_name': 'AssetReference'},
            '_metadata': ('django.db.models.fields.TextField', [], {}),
            'file_id_filename': ('django.db.models.fields.TextField', [], {}),
            'file_id_hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'subname': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'damn_rest.filereference': {
            'Meta': {'object_name': 'FileReference'},
            '_file_description': ('django.db.models.fields.TextField', [], {}),
            '_metadata': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.TextField', [], {}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['damn_rest']