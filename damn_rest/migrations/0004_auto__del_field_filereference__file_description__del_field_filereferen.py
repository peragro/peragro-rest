# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'AssetReference', fields ['file_id_hash', 'subname', 'mimetype']
        db.delete_unique(u'damn_rest_assetreference', ['file_id_hash', 'subname', 'mimetype'])

        # Deleting field 'FileReference._file_description'
        db.delete_column(u'damn_rest_filereference', '_file_description')

        # Deleting field 'FileReference._metadata'
        db.delete_column(u'damn_rest_filereference', '_metadata')

        # Adding field 'FileReference._description'
        db.add_column(u'damn_rest_filereference', '_description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding index on 'FileReference', fields ['hash']
        db.create_index(u'damn_rest_filereference', ['hash'])

        # Deleting field 'AssetReference._metadata'
        db.delete_column(u'damn_rest_assetreference', '_metadata')

        # Deleting field 'AssetReference.file_id_filename'
        db.delete_column(u'damn_rest_assetreference', 'file_id_filename')

        # Deleting field 'AssetReference.file_id_hash'
        db.delete_column(u'damn_rest_assetreference', 'file_id_hash')

        # Adding field 'AssetReference._description'
        db.add_column(u'damn_rest_assetreference', '_description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'AssetReference.file'
        db.add_column(u'damn_rest_assetreference', 'file',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='assets', to=orm['damn_rest.FileReference']),
                      keep_default=False)

        # Adding unique constraint on 'AssetReference', fields ['file', 'subname', 'mimetype']
        db.create_unique(u'damn_rest_assetreference', ['file_id', 'subname', 'mimetype'])


    def backwards(self, orm):
        # Removing unique constraint on 'AssetReference', fields ['file', 'subname', 'mimetype']
        db.delete_unique(u'damn_rest_assetreference', ['file_id', 'subname', 'mimetype'])

        # Removing index on 'FileReference', fields ['hash']
        db.delete_index(u'damn_rest_filereference', ['hash'])

        # Adding field 'FileReference._file_description'
        db.add_column(u'damn_rest_filereference', '_file_description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'FileReference._metadata'
        db.add_column(u'damn_rest_filereference', '_metadata',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Deleting field 'FileReference._description'
        db.delete_column(u'damn_rest_filereference', '_description')

        # Adding field 'AssetReference._metadata'
        db.add_column(u'damn_rest_assetreference', '_metadata',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'AssetReference.file_id_filename'
        raise RuntimeError("Cannot reverse this migration. 'AssetReference.file_id_filename' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'AssetReference.file_id_filename'
        db.add_column(u'damn_rest_assetreference', 'file_id_filename',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'AssetReference.file_id_hash'
        raise RuntimeError("Cannot reverse this migration. 'AssetReference.file_id_hash' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'AssetReference.file_id_hash'
        db.add_column(u'damn_rest_assetreference', 'file_id_hash',
                      self.gf('django.db.models.fields.CharField')(max_length=128),
                      keep_default=False)

        # Deleting field 'AssetReference._description'
        db.delete_column(u'damn_rest_assetreference', '_description')

        # Deleting field 'AssetReference.file'
        db.delete_column(u'damn_rest_assetreference', 'file_id')

        # Adding unique constraint on 'AssetReference', fields ['file_id_hash', 'subname', 'mimetype']
        db.create_unique(u'damn_rest_assetreference', ['file_id_hash', 'subname', 'mimetype'])


    models = {
        u'damn_rest.assetreference': {
            'Meta': {'unique_together': "(('file', 'subname', 'mimetype'),)", 'object_name': 'AssetReference'},
            '_description': ('django.db.models.fields.TextField', [], {}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assets'", 'to': u"orm['damn_rest.FileReference']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'subname': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'damn_rest.filereference': {
            'Meta': {'object_name': 'FileReference'},
            '_description': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.TextField', [], {}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['damn_rest']