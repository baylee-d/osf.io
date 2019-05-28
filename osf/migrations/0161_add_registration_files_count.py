# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-18 14:43
from __future__ import unicode_literals
import logging
import progressbar

from django.db import migrations, models
from django.db.models import Count
from django_bulk_update.helper import bulk_update
from osf.models import Registration

logger = logging.getLogger(__file__)

def add_registration_files_count(state, *args, **kwargs):
    """
    Caches registration files count on Registration object.

    Importing Registration model outside of this method to take advantage of files
    relationship for speed purposes in this migration.  If this model changes significantly,
    this migration may have to be modified in the future so it runs on an empty db.
    """
    registrations = Registration.objects.filter(is_deleted=False).filter(
        files__type='osf.osfstoragefile',
        files__deleted_on__isnull=True
    ).annotate(
        annotated_file_count=Count('files')
    )
    progress_bar = progressbar.ProgressBar(maxval=registrations.count() or 100).start()
    registrations_to_update = []

    for i, registration in enumerate(registrations, 1):
        progress_bar.update(i)
        registration.files_count = registration.annotated_file_count
        registrations_to_update.append(registration)

    bulk_update(registrations_to_update, update_fields=['files_count'], batch_size=5000)
    logger.info('Populated `files_count` on a total of {} registrations'.format(len(registrations_to_update)))
    progress_bar.finish()


def noop(*args, **kwargs):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0160_merge_20190408_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='abstractnode',
            name='files_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(add_registration_files_count, noop)
    ]
