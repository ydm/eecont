#-*- coding: utf-8 -*-

# TODO: use fixtures instead of hard coded dictionaries

from __future__ import unicode_literals

import copy
import datetime

from django.test import TestCase
from django.conf import settings
from django.utils import six
from django.utils import timezone

import pytz

from eecont import inserter
from eecont import models
from eecont import transform


def _dt(*args, **kwargs):
    tz = kwargs.get('tz')
    dt = datetime.datetime(*args)
    if settings.USE_TZ and tz:
        dt = timezone.make_aware(dt, pytz.timezone(tz))
    return dt


########################
# Test transformations #
########################

class TransformTestMixin(object):

    _expected = None
    _input = None
    _func = lambda a: a

    def _time(self, *args):
        return datetime.time(*args)

    @property
    def expected(self):
        return self._expected

    @property
    def input(self):
        return copy.deepcopy(self._input)

    def test_filter(self):
        inp = self.input[0]
        inp['something1'] = 'something else 1'
        inp['something2'] = 'something else 2'
        inp['something3'] = 'something else 3'
        actual = self._func(inp)
        self.assertEqual([self._expected[0]], actual)

    def test_single(self):
        actual = self._func(self.input[0])
        self.assertEqual([self.expected[0]], actual)

    def test_multiple(self):
        actual = self._func(self.input)
        self.assertEqual(self.expected, actual)


class CityTransformTest(TransformTestMixin, TestCase):
    _func = staticmethod(transform.cities)
    _input = [
        {'attach_offices':
             {'cargo_expres_shipments':
                  {'from_door':   {'office_code': ['1000', '1001']},
                   'from_office': {'office_code': ['1002', '1003']},
                   'to_door':     {'office_code': ['1004', '1005']},
                   'to_office':   {'office_code': ['1006', '1007']}},
              'cargo_palet_shipments':
                  {'from_door':   {'office_code': ['1008', '1009']},
                   'from_office': {'office_code': ['1010', '1011']},
                   'to_door':     {'office_code': ['1012', '1013']},
                   'to_office':   {'office_code': ['1014', '1015']}},
              'courier_shipments':
                  {'from_door':   {'office_code': ['1016', '1017']},
                   'from_office': {'office_code': ['1018', '1019']},
                   'to_door':     {'office_code': ['1020', '1021']},
                   'to_office':   {'office_code': ['1022', '1023']}},
              'post_shipments':
                  {'from_door':   {'office_code': ['1024', '1025']},
                   'from_office': {'office_code': ['1026', '1027']},
                   'to_door':     {'office_code': ['1028', '1029']},
                   'to_office':   {'office_code': ['1030', '1031']}}},
         'id': '2000',
         'id_country': '2001',
         'id_office': '2003',
         'id_zone': '2004',
         'name': 'Град №1',
         'name_en': 'City #1',
         'post_code': '2005',
         'region': 'Планета Земя',
         'region_en': 'Planet Earth',
         'service_days': {'day1': '1', 'day2': '1', 'day3': '1', 'day4': '1',
                          'day5': '0', 'day6': '0', 'day7': '0'},
         'type': 'гр.',
         'updated_time': '2012-10-03 09:07:09'},

        {'attach_offices':
             {'cargo_expres_shipments':
                  {'from_door':     {'office_code': ''},
                   'from_office': '',
                   'to_door':       {'office_code': ['2000', '2001']},
                   'to_office':     {'office_code': ['2002', '2003']}},
              # 'cargo_palet_shipments':
              #     {'from_door':   {'office_code': ['2004', '2005']},
              #      'from_office': {'office_code': ['2006', '2007']},
              #      'to_door':     {'office_code': ['2008', '2009']},
              #      'to_office':   {'office_code': ['2010', '2011']}},
              'courier_shipments': '',
                  # {'from_door':   {'office_code': ['2012', '2013']},
                  #  'from_office': {'office_code': ['2014', '2015']},
                  #  'to_door':     {'office_code': ['2016', '2017']},
                  #  'to_office':   {'office_code': ['2018', '2019']}},
              'post_shipments':
                  {'from_door':     {'office_code': ['2020', '2021']},
                   # 'from_office': {'office_code': ['2022', '2023']},
                   'to_door':       {'office_code': []},
                   'to_office':     {'office_code': ['2025', '2026', '2027']}}},
         'id': '3000',
         'id_country': '3001',
         'id_office': '3002',
         'id_zone': '3003',
         'name': 'Град №2',
         'name_en': 'City #2',
         'post_code': '3004',
         'region': 'Планета Земя',
         'region_en': 'Planet Earth',
         'service_days': {'day1': '0', 'day2': '0', 'day3': '0', 'day4': '0',
                          'day5': '1', 'day6': '1', 'day7': '1'},
         'type': 'с.',
         'updated_time': '2009-09-09 23:59:59'}]

    def setUp(self):
        self._expected = [
            {'eid': 2000,
             # we can't match a country by its id
             # office
             'zone': 2004,
             'name': 'Град №1',
             'name_en': 'City #1',
             'post_code': 2005,
             # TODO: region?
             'service_days': [True, True, True, True, False, False, False],
             'is_village': False,
             'updated_time': _dt(2012, 10, 3, 9, 7, 9, tz='Europe/Sofia'),

             'ces_from_door': [1000, 1001], 'ces_from_office': [1002, 1003],
             'ces_to_door': [1004, 1005], 'ces_to_office': [1006, 1007],

             'cps_from_door': [1008, 1009], 'cps_from_office': [1010, 1011],
             'cps_to_door': [1012, 1013], 'cps_to_office': [1014, 1015],

             'cs_from_door': [1016, 1017], 'cs_from_office': [1018, 1019],
             'cs_to_door': [1020, 1021], 'cs_to_office': [1022, 1023],

             'ps_from_door': [1024, 1025], 'ps_from_office': [1026, 1027],
             'ps_to_door': [1028, 1029], 'ps_to_office': [1030, 1031]},

            {'eid': 3000,
             # we can't match a country by its id
             # office
             'zone': 3003,
             'name': 'Град №2',
             'name_en': 'City #2',
             'post_code': 3004,
             # TODO: region?
             'service_days': [False, False, False, False, True, True, True],
             'is_village': True,
             'updated_time': _dt(2009, 9, 9, 23, 59, 59, tz='Europe/Sofia'),

             'ces_from_door': [], 'ces_from_office': [],
             'ces_to_door': [2000, 2001], 'ces_to_office': [2002, 2003],

             'cps_from_door': [], 'cps_from_office': [],
             'cps_to_door': [], 'cps_to_office': [],

             'cs_from_door': [], 'cs_from_office': [],
             'cs_to_door': [], 'cs_to_office': [],

             'ps_from_door': [2020, 2021], 'ps_from_office': [],
             'ps_to_door': [], 'ps_to_office': [2025, 2026, 2027]}]


class CountryTransformTest(TestCase, TransformTestMixin):
    _func = staticmethod(transform.countries)
    _input = [
        {'country_name': 'Държава №1',
         'country_name_en': 'Country #1',
         'id_zone': '1000',
         'zone_name': 'Зона №1',
         'zone_name_en': 'Zone #1'},
        {'country_name': 'Държава №2',
         'country_name_en': 'Country #2',
         'id_zone': '2000',
         'zone_name': 'Зона №2',
         'zone_name_en': 'Zone #2'}]
    _expected = [
        {'name': 'Държава №1',
         'name_en': 'Country #1',
         'zone': 1000},
        {'name': 'Държава №2',
         'name_en': 'Country #2',
         'zone': 2000}]


class OfficeTransformTest(TestCase, TransformTestMixin):
    _func = staticmethod(transform.offices)
    _input = [
        {
         'address': 'Ямбол Ямбол ул. Дружба №1',
         'address_details': {'ap': '',
                             'bl': '',
                             'et': '',
                             'num': '1',
                             'other': '',
                             'quarter_name': 'Ямбол',
                             'street_name': 'ул. Дружба',
                             'vh': ''},
         'address_en': 'Yambol Qmbol ul. Druzhba #1',
         'city_name': 'Ямбол',
         'city_name_en': 'Yambol',
         'id': '648',
         'latitude': '42.4821587',
         'longitude': '26.4996131',
         'name': 'Ямбол Трите вятъра',
         'name_en': 'Yambol Trite vjatara',
         'office_code': '8603',
         'phone': '+359 466 29962,+359 87 9922914',
         'time_priority': '09:30:00',
         'updated_time': '2013-03-24 01:00:13',
         'work_begin': '09:00:00',
         'work_begin_saturday': '09:00:00',
         'work_end': '18:00:00',
         'work_end_saturday': '13:00:00'},

        {'address': 'Тутракан Тутракан ул. Силистра №51',
         'address_details': {'ap': '123',
                             'bl': '234',
                             'et': '345',
                             'num': '51',
                             'other': 'Пепеляшка е красива',
                             'quarter_name': 'Тутракан',
                             'street_name': 'ул. Силистра',
                             'vh': '456'},
         'address_en': 'Tutrakan Tutrakan ul. Silistra #1',
         'city_name': 'Тутракан',
         'city_name_en': 'Tutrakan',
         'id': '177',
         'latitude': '44.04661273118875',
         'longitude': '26.624570750656133',
         'name': 'Тутракан',
         'name_en': 'Tutrakan',
         'office_code': '7600',
         'phone': '+359 866 61464,+359 87 9922602',
         'time_priority': '23:34:45',
         'updated_time': '2013-03-10 13:26:00',
         'work_begin': '12:23:34',
         'work_begin_saturday': '23:23:23',
         'work_end': '12:34:56',
         'work_end_saturday': '20:01:02'}]

    def setUp(self):
        self._expected = [
            {'address': 'Ямбол Ямбол ул. Дружба №1',
             'address_en': 'Yambol Qmbol ul. Druzhba #1',
             'apartment': '',
             'apartment_building': '',
             'city_name': 'Ямбол',
             'city_name_en': 'Yambol',
             'eid': 648,
             'entrance': '',
             'floor': '',
             'latitude': '42.4821587',
             'longitude': '26.4996131',
             'name': 'Ямбол Трите вятъра',
             'name_en': 'Yambol Trite vjatara',
             'number': '1',
             'office_code': 8603,
             'other': '',
             'phone': '+359 466 29962,+359 87 9922914',
             'quarter_name': 'Ямбол',
             'street_name': 'ул. Дружба',
             'time_priority': self._time(9, 30),
             'updated_time': _dt(2013, 3, 24, 1, 0, 13, tz='Europe/Sofia'),
             'work_begin': self._time(9),
             'work_begin_saturday': self._time(9),
             'work_end': self._time(18),
             'work_end_saturday': self._time(13)},

            {'address': 'Тутракан Тутракан ул. Силистра №51',
             'address_en': 'Tutrakan Tutrakan ul. Silistra #1',
             'apartment': '123',
             'apartment_building': '234',
             'city_name': 'Тутракан',
             'city_name_en': 'Tutrakan',
             'eid': 177,
             'entrance': '456',
             'floor': '345',
             'latitude': '44.04661273118875',
             'longitude': '26.624570750656133',
             'name': 'Тутракан',
             'name_en': 'Tutrakan',
             'number': '51',
             'office_code': 7600,
             'other': 'Пепеляшка е красива',
             'phone': '+359 866 61464,+359 87 9922602',
             'quarter_name': 'Тутракан',
             'street_name': 'ул. Силистра',
             'time_priority': self._time(23, 34, 45),
             'updated_time': _dt(2013, 03, 10, 13, 26, 00, tz='Europe/Sofia'),
             'work_begin': self._time(12, 23, 34),
             'work_begin_saturday': self._time(23, 23, 23),
             'work_end': self._time(12, 34, 56),
             'work_end_saturday': self._time(20, 01, 02)}]


class RegionTransformTest(TestCase, TransformTestMixin):
    _func = staticmethod(transform.regions)
    _input = [
        {'id': '1000',
         'name': 'Име на регион №1',
         'code': '1001',
         'id_city': '1002',
         'updated_time': '2010-9-15 7:15:30'},
        {'id': '2000',
         'name': 'Име на регион №2',
         'code': '2001',
         'id_city': '2002',
         'updated_time': '2010-12-8 22:33:44'}]

    def setUp(self):
        self._expected = [
            {'eid': 1000,
             'name': 'Име на регион №1',
             'code': 1001,
             'city': 1002,
             'updated_time': _dt(2010, 9, 15, 7, 15, 30,
                                      tz='Europe/Sofia')},
            {'eid': 2000,
             'name': 'Име на регион №2',
             'code': 2001,
             'city': 2002,
             'updated_time': _dt(2010, 12, 8, 22, 33, 44,
                                      tz='Europe/Sofia')}]
    

class StreetTransformTest(TestCase, TransformTestMixin):
    _func = staticmethod(transform.streets)
    _input = [
        {'id': '1001',
         'name': 'ул. Някоя си',
         'name_en': 'Something Str.',
         'city_post_code': '1002',
         'id_city': '1003',
         'updated_time': '2000-10-20 10:20:30'},
        {'id': '2001',
         'name': 'ул. Другая си',
         'name_en': 'Something Else Str.',
         'city_post_code': '2002',
         'id_city': '2003',
         'updated_time': '2001-11-21 11:21:31'}]

    def setUp(self):
        self._expected = [
            {'eid': 1001,
             'name': 'ул. Някоя си',
             'name_en': 'Something Str.',
             # 'city_post_code': 1002,
             'city': 1003,
             'updated_time': _dt(2000, 10, 20, 10, 20, 30,
                                      tz='Europe/Sofia')},
            {'eid': 2001,
             'name': 'ул. Другая си',
             'name_en': 'Something Else Str.',
             # 'city_post_code': 2002,
             'city': 2003,
             'updated_time': _dt(2001, 11, 21, 11, 21, 31,
                                      tz='Europe/Sofia')}]


class ZoneTransformTest(TestCase, TransformTestMixin):
    _func = staticmethod(transform.zones)
    _input = [
        {'id': '1000',
         'is_ee': '1',
         'name': 'Име1',
         'name_en': 'Name1',
         'national': '1',
         'updated_time': '2013-02-18 12:13:14'},
        {'id': '2000',
         'is_ee': '0',
         'name': 'Име2',
         'name_en': 'Name2',
         'national': '0',
         'updated_time': '2000-02-29 23:24:25'}]

    def setUp(self):
        tz = 'Europe/Sofia'
        self._expected = [
            {'eid': 1000,
             'is_ee': True,
             'name': 'Име1',
             'name_en': 'Name1',
             'national': True,
             'updated_time':
                 _dt(2013, 2, 18, 12, 13, 14, tz=tz)},
            {'eid': 2000,
             'is_ee': False,
             'name': 'Име2',
             'name_en': 'Name2',
             'national': False,
             'updated_time':
                 _dt(2000, 2, 29, 23, 24, 25, tz=tz)}]


    # TODO: test isn't completed
    def test_invalid(self):
        inp = self.input[0]
        inp['id'] = 'bad'
        self.assertRaises(ValueError, transform.zones, inp)


######################################
# Test populating of related objects #
######################################

class PopulateRelationsTest(TestCase):

    def _create_city(self, zone_eid, eid=1000):
        return models.City.objects.create(
            eid=eid,
            zone=models.Zone.objects.get(eid=zone_eid),
            name='Градец', name_en='Gradets',
            post_code=1000,
            service_days=[True] * 7,
            is_village=True,
            updated_time=_dt(2012, 10, 10, tz='Europe/Sofia'),

            ces_from_door=[], ces_to_door=[],
            ces_from_office=[], ces_to_office=[],

            cps_from_door=[], cps_to_door=[],
            cps_from_office=[], cps_to_office=[],

            cs_from_door=[], cs_to_door=[],
            cs_from_office=[], cs_to_office=[],

            ps_from_door=[], ps_to_door=[],
            ps_from_office=[], ps_to_office=[])

    def _create_country(self, zone_eid, name):
        return models.Country.objects.create(
            name=name,
            name_en='Name in latin',
            zone=models.Zone.objects.get(eid=zone_eid))

    def _create_office(self, eid=1001):
        return models.Office.objects.create(
            eid=eid,
            name='Офисно име', name_en='Office name',
            office_code=1337,
            phone='',
            time_priority='11:30',
            latitude='',
            longitude='',
            work_begin='9:00',
            work_end='17:00',
            work_begin_saturday='10:00',
            work_end_saturday='14:00',
            updated_time=_dt(1988, 10, 4, tz='Europe/Sofia'),

            # Адрес
            address='ул. Клокотница №7',
            address_en='ul. Klokotnitsa No7',
            city_name='София',
            city_name_en='Sofia',
            quarter_name='кв. Овча купер',
            street_name='ул. Клокотница',
            number='7',
            apartment_building='',
            entrance='',
            floor='',
            apartment='',
            other='')

    def _create_quarter(self, city_eid, eid=1002):
        return models.Quarter.objects.create(
            eid=eid,
            name='Някой си', name_en='Nyakoi si',
            city=models.City.objects.get(eid=city_eid),
            updated_time=_dt(1990, 4, 10, tz='Europe/Sofia'))

    def _create_street(self, city_eid, eid=1003):
        return self._create_quarter(city_eid, eid)

    def _create_zone(self, eid=1000):
        return models.Zone.objects.create(
            eid=eid,
            is_ee=True,
            name='Някаква зона',
            name_en='A zone',
            national=True,
            updated_time=_dt(2012, 10, 04, tz='Europe/Sofia'))

    def test_city(self):
        expected_city = self._create_city(self._create_zone().eid)
        data = {'city': expected_city.eid}
        inserter.populate_relations(data)
        self.assertEqual(expected_city, data['city'])

    def test_country(self):
        expected_country = self._create_country(self._create_zone().eid,
                                                'България')
        data = {'country': 'България'}
        inserter.populate_relations(data)
        self.assertEqual(expected_country, data['country'])

    def test_office(self):
        expected = self._create_office()
        data = {'office': expected.eid}
        inserter.populate_relations(data)
        self.assertEqual(expected, data['office'])

    # TODO
    def test_quarter(self):
        pass

    def test_street(self):
        pass

    def test_zone(self):
        expected_zone = self._create_zone()
        data = {'zone': expected_zone.eid}
        inserter.populate_relations(data)
        self.assertEqual(expected_zone, data['zone'])


class InserterTest(TestCase):

    _zone = {
        'eid': 1000,
        'is_ee': True,
        'name': 'Име1',
        'name_en': 'Name1',
        'national': True,
        'updated_time': _dt(2013, 2, 18, 12, 13, 14, tz='Europe/Sofia')}
    
    _city = {
        'eid': 2000,
        'zone': 1000,
        'name': 'Град №1',
        'name_en': 'City #1',
        'post_code': 2005,
        'service_days': [True, True, True, True, False, False, False],
        'is_village': False,
        'updated_time': _dt(2012, 10, 3, 9, 7, 9, tz='Europe/Sofia'),

        'ces_from_door': [1000, 1001], 'ces_from_office': [1002, 1003],
        'ces_to_door': [1004, 1005], 'ces_to_office': [1006, 1007],

        'cps_from_door': [1008, 1009], 'cps_from_office': [1010, 1011],
        'cps_to_door': [1012, 1013], 'cps_to_office': [1014, 1015],

        'cs_from_door': [1016, 1017], 'cs_from_office': [1018, 1019],
        'cs_to_door': [1020, 1021], 'cs_to_office': [1022, 1023],

        'ps_from_door': [1024, 1025], 'ps_from_office': [1026, 1027],
        'ps_to_door': [1028, 1029], 'ps_to_office': [1030, 1031]}

    def _insert_zone(self):
        data = copy.deepcopy(self._zone)
        inserter.insert(data, 'Zone', 'eid')
        obj = models.Zone.objects.get(eid=self._zone['eid'])
        return obj

    def _insert_city(self):
        data = copy.deepcopy(self._city)
        inserter.insert(data, 'City', 'eid')
        obj = models.City.objects.get(eid=self._city['eid'])
        return obj

    def test_inserter_zone(self):
        zone_obj = self._insert_zone()
        for k, v in six.iteritems(self._zone):
            self.assertEqual(v, getattr(zone_obj, k))

    def test_inserter_city(self):
        zone_obj = self._insert_zone()
        city_obj = self._insert_city()

        data = copy.deepcopy(self._city)
        data['zone'] = zone_obj

        for k, v in six.iteritems(data):
            self.assertEqual(v, getattr(city_obj, k))


class OfficeDefaultsTest(TestCase):

    _input = [{
        'address': 'Ямбол Ямбол ул. Дружба №1',
        'address_details': {'ap': '',
                            'bl': '',
                            'et': '',
                            'num': '1',
                            'other': '',
                            'quarter_name': 'Ямбол',
                            'street_name': 'ул. Дружба',
                            'vh': ''},
        'address_en': 'Yambol Qmbol ul. Druzhba #1',
        'city_name': 'Ямбол',
        'city_name_en': 'Yambol',
        'id': '648',
        'latitude': '42.4821587',
        'longitude': '26.4996131',
        'name': 'Ямбол Трите вятъра',
        'name_en': 'Yambol Trite vjatara',
        'office_code': '8603',
        'phone': '+359 466 29962,+359 87 9922914',
        'updated_time': '2013-03-24 01:00:13',

        'time_priority': None,
        'work_begin': None,
        'work_begin_saturday': None,
        'work_end': None,
        'work_end_saturday': None}]

    _expected = [{
            'address': 'Ямбол Ямбол ул. Дружба №1',
            'address_en': 'Yambol Qmbol ul. Druzhba #1',
            'apartment': '',
            'apartment_building': '',
            'city_name': 'Ямбол',
            'city_name_en': 'Yambol',
            'eid': 648,
            'entrance': '',
            'floor': '',
            'latitude': '42.4821587',
            'longitude': '26.4996131',
            'name': 'Ямбол Трите вятъра',
            'name_en': 'Yambol Trite vjatara',
            'number': '1',
            'office_code': 8603,
            'other': '',
            'phone': '+359 466 29962,+359 87 9922914',
            'quarter_name': 'Ямбол',
            'street_name': 'ул. Дружба',
            'updated_time': _dt(2013, 3, 24, 1, 0, 13, tz='Europe/Sofia'),

            'time_priority': datetime.time(0, 0),
            'work_begin': datetime.time(0, 0),
            'work_begin_saturday': datetime.time(0, 0),
            'work_end': datetime.time(0, 0),
            'work_end_saturday': datetime.time(0, 0)}]

    def test_default_values(self):
        data = transform.offices(copy.deepcopy(self._input))
        self.assertEqual(self._expected, data)
