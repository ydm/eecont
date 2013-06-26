#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import collections
import datetime
import sys

from django.conf import settings
from django.utils import dateparse
from django.utils import six
from django.utils.six import print_
from django.utils import timezone

import pytz

CITY_FIELDS = ['eid', 'zone', 'name', 'name_en', 'post_code', 'service_days',
               'is_village', 'updated_time',
               'ces_from_door', 'ces_to_door', 'ces_from_office',
               'ces_to_office',
               'cps_from_door', 'cps_to_door', 'cps_from_office',
               'cps_to_office',
               'cs_from_door', 'cs_to_door', 'cs_from_office', 'cs_to_office',
               'ps_from_door', 'ps_to_door', 'ps_from_office', 'ps_to_office']

COUNTRY_FILEDS = ['name', 'name_en', 'zone']

OFFICE_FIELDS = ['address', 'address_en', 'city_name', 'city_name_en', #'city',
                 'quarter_name', 'quarter', 'street_name', 'street', 'number',
                 'apartment_building', 'entrance', 'floor', 'apartment',
                 'other', 'name', 'name_en', 'office_code', 'phone',
                 'time_priority', 'latitude', 'longitude', 'work_begin',
                 'work_end', 'work_begin_saturday', 'work_end_saturday',
                 'updated_time', 'eid']

REGION_FIELDS = ['eid', 'name', 'code', 'city', 'updated_time']
STREET_FIELDS = ['eid', 'name', 'name_en', 'city', 'updated_time']
ZONE_FIELDS = ['eid', 'is_ee', 'name', 'name_en', 'national', 'updated_time']


def _address_details(d):
    d = d.get('address_details', d)

    # Copy these keys
    ret = {k: d[k] for k in ['other', 'quarter_name', 'street_name']}

    # And transform these
    ret['apartment_building'] = d.get('bl')
    ret['entrance'] = d.get('vh')
    ret['floor'] = d.get('et')
    ret['apartment'] = d.get('ap')
    ret['number'] = d.get('num')
    return ret


def _time(val, default=None):
    if not val:
        val = ''
    
    # Handle the special case of '24:00'
    if val[:2] == '24':
        val = '23:59'

    ret = None
    try:
        ret = dateparse.parse_time(val)
    except ValueError as e:
        print_('Bad time string: {}'.format(val), file=sys.stderr)
        six.reraise(ValueError, e)

    if isinstance(ret, datetime.time):
        return ret
    if default is not None:
        return _time(default)
    return None


def _updated_time(value):
    try:
        dt = dateparse.parse_datetime(value)
        if settings.USE_TZ and not timezone.is_aware(dt):
            dt = timezone.make_aware(dt, pytz.timezone('Europe/Sofia'))
        return dt
    except ValueError:
        # Just return a date that's really long in the past
        # raise e
        return timezone.make_aware(datetime.datetime(2000, 01, 01),
                                   timezone.utc)


def _service_days(d):
    return [d['day{}'.format(i)] == '1' for i in range(1,8)]


def _attach_offices(data, tag1, tag2):
    offices = data.get('attach_offices', data)

    res = offices.get(tag1)
    if not isinstance(res, collections.Mapping): return []

    res = res.get(tag2)
    if not isinstance(res, collections.Mapping): return []

    res = res.get('office_code')
    if not isinstance(res, list): return []

    return [int(s) for s in res]


def _clean(dct, keys):
    """Remove all keys in `dct` that are not found in `keys`."""

    # Remove unwanted keys
    for k in [e for e in six.iterkeys(dct) if e not in keys]:
        del dct[k]


##############
# Public API #
##############

def cities(data):
    if not isinstance(data, list):
        data = [data]

    tags = {
        'ces': 'cargo_expres_shipments',
        'cps': 'cargo_palet_shipments',
        'cs' : 'courier_shipments',
        'ps' : 'post_shipments'}

    for city in data:
        city['eid'] = int(city.pop('id'))
        city['is_village'] = city.pop('type') == 'с.'
        city['post_code'] = int(city['post_code'])
        city['service_days'] = _service_days(city['service_days'])
        city['updated_time'] = _updated_time(city['updated_time'])
        city['zone'] = int(city.pop('id_zone'))

        # Office codes
        for prefix, tag1 in six.iteritems(tags):
            for seg1 in ['from', 'to']:
                for seg2 in ['door', 'office']:
                    tag2 = '{}_{}'.format(seg1, seg2)
                    key = '{}_{}'.format(prefix, tag2)
                    city[key] = _attach_offices(city, tag1, tag2)

        _clean(city, CITY_FIELDS)
    return data


def countries(data):
    if not isinstance(data, list):
        data = [data]
    for country in data:
        country['name'] = country.pop('country_name')
        country['name_en'] = country.pop('country_name_en')
        country['zone'] = int(country.pop('id_zone'))
        _clean(country, COUNTRY_FILEDS)
    return data


def offices(data):
    if not isinstance(data, list):
        data = [data]
    for o in data:
        # Leave the following fields as they are:
        # address, address_en, city_name, city_name_en, name, name_en,
        # phone

        o.update(_address_details(o))
        o['eid'] = int(o['id'])
        o['latitude'] = o['latitude']
        o['longitude'] = o['longitude']
        o['office_code'] = int(o['office_code'])
        o['updated_time'] = _updated_time(o['updated_time'])

        o['time_priority']       = _time(o['time_priority']      , '0:0')
        o['work_begin']          = _time(o['work_begin']         , '0:0')
        o['work_begin_saturday'] = _time(o['work_begin_saturday'], '0:0')
        o['work_end']            = _time(o['work_end']           , '0:0')
        o['work_end_saturday']   = _time(o['work_end_saturday']  , '0:0')
        _clean(o, OFFICE_FIELDS)
        # _populate_missing(o, OFFICE_DEFAULTS)
    return data


def quarters(data):
    # It's the same model as `streets`
    return streets(data)


def regions(data):
    if not isinstance(data, list):
        data = [data]
    for rgn in data:
        rgn['eid'] = int(rgn.pop('id'))
        rgn['code'] = int(rgn.pop('code'))
        rgn['city'] = int(rgn.pop('id_city'))
        rgn['updated_time'] = _updated_time(rgn['updated_time'])
        _clean(rgn, REGION_FIELDS)
    return data


def streets(data):
    if not isinstance(data, list):
        data = [data]
    for street in data:
        street['eid'] = int(street.pop('id'))
        street['city'] = int(street['id_city'])
        street['updated_time'] = _updated_time(street['updated_time'])
        _clean(street, STREET_FIELDS)
    return data


def zones(data):
    if not isinstance(data, list):
        data = [data]
    for zone in data:
        zone['eid'] = int(zone.pop('id'))
        zone['is_ee'] = zone['is_ee'] == '1'
        zone['national'] = zone['national'] == '1'
        zone['updated_time'] = _updated_time(zone['updated_time'])
        _clean(zone, ZONE_FIELDS)
    return data
