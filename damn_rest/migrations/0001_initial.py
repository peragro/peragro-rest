# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-21 21:50


from __future__ import absolute_import
import damn_rest.models
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_project', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_description', models.TextField()),
                ('subname', models.CharField(max_length=255)),
                ('mimetype', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.TextField(db_index=True)),
            ],
            bases=(damn_rest.models.VersionMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FileReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_description', models.TextField()),
                ('filename', models.TextField()),
                ('hash', models.CharField(db_index=True, max_length=128)),
                ('mimetype', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(damn_rest.models.VersionMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('fullname', models.TextField(editable=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='damn_rest.Path')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paths', to='django_project.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='filereference',
            name='path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='damn_rest.Path'),
        ),
        migrations.AddField(
            model_name='filereference',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='django_project.Project'),
        ),
        migrations.AddField(
            model_name='assetreference',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='damn_rest.FileReference'),
        ),
        migrations.AlterUniqueTogether(
            name='assetreference',
            unique_together=set([('file', 'subname', 'mimetype')]),
        ),
    ]
