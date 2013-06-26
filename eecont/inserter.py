#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import collections
import sys

from django.core import exceptions
from django.utils import six
from django.utils.six import print_

from eecont import models
from eecont import transform
import remoteecont


###############
# Log Helpers #
###############

def _log(s, verbosity, priority):
    if priority <= verbosity:
        print_(s)


def _log_general(msg, verbosity=1, priority=1):
    _log(msg, verbosity, priority)


def _log_insert(obj, verbosity=1, priority=2):
    _log('Insert: {}'.format(obj), verbosity, priority)


def _log_update(obj, verbosity=1, priority=2):
    _log('Update: {}'.format(obj), verbosity, priority)


##################
# Insert helpers #
##################

def _get_obj(model, unique_key, unique_val):
    lookup = {unique_key: unique_val}
    try:
        return model.objects.get(**lookup)
    except model.DoesNotExist as e:
        # ...
        raise e


def populate_relations(data):
    # TODO: repetition, see `orders` in fetch_and_insert
    model2unique = {
        'zone':    {'model': models.Zone,    'unique': 'eid'},
        'country': {'model': models.Country, 'unique': 'name'},
        'city':    {'model': models.City,    'unique': 'eid'},
        'quarter': {'model': models.Quarter, 'unique': 'eid'},
        'street':  {'model': models.Street,  'unique': 'eid'},
        'office':  {'model': models.Office,  'unique': 'eid'}}

    for name, v in six.iteritems(model2unique):
        if name in data:
            data[name] = _get_obj(v['model'], v['unique'], data[name])
    return data


#############
# Inserters #
#############

def insert(data, model, unique_field, verbosity=1):
    if isinstance(model, six.text_type):
        model = getattr(models, model)

    data = populate_relations(data)
    args = {unique_field: data.pop(unique_field),
            'defaults': data}

    obj, created = model.objects.get_or_create(**args)

    if created:
        _log_insert(obj, verbosity)
    else:
        for k, v in six.iteritems(data):
            setattr(obj, k, v)
        obj.save()
        _log_update(obj, verbosity)


def fetch_and_insert(**kwargs):
    which       = kwargs['which'] # which models to fetch & insert
    parcel_url  = kwargs['parcel_url']
    service_url = kwargs['service_url']
    username    = kwargs['username']
    password    = kwargs['password']
    verbosity   = kwargs['verbosity']

    econt = remoteecont.RemoteEcontXml(
        service_url, parcel_url, username, password, remoteecont.CurlTransfer)

    order = collections.OrderedDict(
        [('zone', {'model': models.Zone, 'fget': econt.cities_zones,
                   'ftransform': transform.zones, 'unique': 'eid'}),

         ('country', {'model': models.Country, 'fget': econt.countries,
                      'ftransform': transform.countries, 'unique': 'name'}),

         ('city', {'model': models.City, 'fget': econt.cities,
                   'ftransform': transform.cities, 'unique': 'eid'}),

         ('quarter', {'model': models.Quarter, 'fget': econt.cities_quarters,
                      'ftransform': transform.quarters, 'unique': 'eid'}),

         ('street', {'model': models.Street, 'fget': econt.cities_streets,
                     'ftransform': transform.streets, 'unique': 'eid'}),

         ('office', {'model': models.Office, 'fget': econt.offices,
                     'ftransform': transform.offices, 'unique': 'eid'})])

    which = which or order.keys()
    f = lambda t: t[0] in which

    for m, v in filter(f, six.iteritems(order)):
        _log_general('Now processing: {}'.format(m), verbosity)

        data = v['fget']()
        _log_general('\tFetched: {} entries'.format(len(data)), verbosity)

        data = v['ftransform'](data)
        _log_general('\t{} data successfully transformed'.format(
                m.capitalize()), verbosity)

        _log_general('\tInserting {} data'.format(m.capitalize()))
        for entry in data:
            try:
                insert(entry, v['model'], v['unique'], verbosity=verbosity)
            except exceptions.ObjectDoesNotExist as e:
                _log_general('\tError while inserting an {}: {}'.format(m, e),
                             verbosity)
