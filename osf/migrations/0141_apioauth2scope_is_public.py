# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-18 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0140_auto_20181018_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='apioauth2scope',
            name='is_public',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
