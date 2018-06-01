# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-10 14:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0098_merge_20180416_1807'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileVersionUserMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('file_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osf.FileVersion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='fileversion',
            name='seen_by',
            field=models.ManyToManyField(related_name='versions_seen', through='osf.FileVersionUserMetadata', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='fileversionusermetadata',
            unique_together=set([('user', 'file_version')]),
        ),
    ]
