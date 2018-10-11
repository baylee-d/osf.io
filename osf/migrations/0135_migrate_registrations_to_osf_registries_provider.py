# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-18 13:51
from __future__ import unicode_literals
import logging

from django.db import migrations

logger = logging.getLogger(__file__)

def migrate_existing_registrations_into_osf_registries(state, schema):
    AbstractProvider = state.get_model('osf', 'abstractprovider')
    AbstractNode = state.get_model('osf', 'abstractnode')
    DraftRegistration = state.get_model('osf', 'draftregistration')

    try:
        osf_registries = AbstractProvider.objects.get(_id='osf', type='osf.registrationprovider')
    except AbstractProvider.DoesNotExist:
        # Allow test / local dev DBs to pass
        logger.warn('Unable to find OSF Registries provider - assuming test environment.')
        pass
    else:
        draft_registrations = DraftRegistration.objects.all()
        registrations = AbstractNode.objects.filter(type='osf.registration')

        updated_drafts = draft_registrations.update(provider_id=osf_registries.id)
        updated_registrations = registrations.update(provider_id=osf_registries.id)

        assert (updated_drafts, updated_registrations) == (draft_registrations.count(), registrations.count())
        logger.info('Successfully migrated {} draft registrations and {} public registrations into OSFRegistries'.format(updated_drafts, updated_registrations))

def remove_existing_registrations_from_osf_registries(state, schema):
    AbstractProvider = state.get_model('osf', 'abstractprovider')
    try:
        osf_registries = AbstractProvider.objects.get(_id='osf', type='osf.registrationprovider')
    except AbstractProvider.DoesNotExist:
        pass
    else:
        total_registrations = osf_registries.registrations.count() + osf_registries.draft_registrations.count()

        osf_registries.draft_registrations.clear()
        osf_registries.registrations.clear()

        logger.info('Successfully removed {} public and draft registrations from OSFRegistries'.format(total_registrations))

class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0134_add_provider_reg_fks'),
    ]

    operations = [
        migrations.RunPython(
            migrate_existing_registrations_into_osf_registries,
            remove_existing_registrations_from_osf_registries
        )
    ]
