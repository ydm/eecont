# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from eecont import fields


# Zones should be imported first
@python_2_unicode_compatible
class Zone(models.Model):

    # Еконтски идентификатор
    eid = models.PositiveIntegerField(unique=True) 

    is_ee = models.BooleanField()          # Еконт или подизпълнител
    name = models.CharField(max_length=100) # име
    name_en = models.CharField(max_length=100) # име на латиница
    national = models.BooleanField()      # българска или международна
    updated_time = models.DateTimeField() # последна редакция на данните

    def __str__(self):
        return 'Zone: {}'.format(self.name)


# Countries - second
@python_2_unicode_compatible
class Country(models.Model):

    # Countries don't have an `id` identifier.  That's why the `name`
    # field is made unique.
    name = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone)

    def __str__(self):
        return 'Country: {}'.format(self.name)


# Cities - third
@python_2_unicode_compatible
class City(models.Model):

    DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sunday']

    eid = models.PositiveIntegerField() # Econt id
    
    # The Econt service provides us with city data with an element
    # called <id_country> which has the id of the country this city
    # belongs to.  The funny thing is the country data has no <id>
    # element, hence we can't use the country id we receive along with
    # the city data.
    # country = models.ForeignKey(Country)

    # office = None # TODO
    zone = models.ForeignKey(Zone)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    post_code = models.PositiveIntegerField()
    # region = models.ForeignKey(Region) # TODO
    service_days = fields.WeekDaysField()
    is_village = models.BooleanField() # this corresponds to <type>
    updated_time = models.DateTimeField()

    # ces = cargo express shipments
    ces_from_door = fields.OfficeListField()
    ces_to_door   = fields.OfficeListField()
    ces_from_office = fields.OfficeListField()
    ces_to_office   = fields.OfficeListField()

    # cps = cargo palet shipments
    cps_from_door = fields.OfficeListField()
    cps_to_door   = fields.OfficeListField()
    cps_from_office = fields.OfficeListField()
    cps_to_office   = fields.OfficeListField()

    # cs = courier shipments
    cs_from_door = fields.OfficeListField()
    cs_to_door   = fields.OfficeListField()
    cs_from_office = fields.OfficeListField()
    cs_to_office   = fields.OfficeListField()

    # ps = post shipments
    ps_from_door  = fields.OfficeListField()
    ps_to_door    = fields.OfficeListField()
    ps_from_office  = fields.OfficeListField()
    ps_to_office    = fields.OfficeListField()

    def __str__(self):
        return 'City: {}'.format(self.name)

    def __getattr__(self, name):
        """
        Provide an easy way to access service days.  Like this:
        city.sd_monday, city.sd_tuesday, city.sd_wednesday, etc.
        """
        prefix = 'sd_'
        if name.startswith(prefix):
            name = name[len(prefix):]
            index = self.DAYS.index(name)
            if len(self.service_days) > index:
                return self.service_days[index]
            else:
                # raise error?
                return False
        else:
            raise AttributeError('getattr: {}'.format(name))


@python_2_unicode_compatible
class Quarter(models.Model):

    eid = models.PositiveIntegerField(unique=True)

    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    # city_post_code --> No need since we have the city at hand
    city = models.ForeignKey(City)
    updated_time = models.DateTimeField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Street(models.Model):

    eid = models.PositiveIntegerField(unique=True)

    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    # city_post_code --> No need since we have the city at hand
    city = models.ForeignKey(City)
    updated_time = models.DateTimeField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Office(models.Model):

    eid = models.PositiveIntegerField()

    # Office data
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    office_code = models.PositiveIntegerField()
    phone = models.CharField(blank=True, max_length=100)

    # Какво?!  В документацията пише: "минимален приоритетен час".
    # Това на мен, като на средно интелигентен човек, нищо не ми
    # говори...
    time_priority = models.TimeField()

    # Geolocation (stored in char fields instead of float fields)
    latitude = models.CharField(blank=True, max_length=20)
    longitude = models.CharField(blank=True, max_length=20)

    # Work hours
    work_begin = models.TimeField()
    work_end = models.TimeField()

    # Saturday work hours
    work_begin_saturday = models.TimeField()
    work_end_saturday = models.TimeField()

    # Meta
    updated_time = models.DateTimeField()

    # Address

    # full address
    address = models.CharField(max_length=127)
    address_en = models.CharField(max_length=127)

    # XXX: Do we really need the ForeignKeys? Is the Econt API
    # consistent enough?
    city_name = models.CharField(max_length=100)
    city_name_en = models.CharField(max_length=100)
    # city = models.ForeignKey(City, null=True)

    quarter_name = models.CharField(blank=True, max_length=100)
    # quarter = models.ForeignKey(Quarter, blank=True) # <id_quarter>

    street_name = models.CharField(max_length=100)
    # street = models.ForeignKey(Street)   # <id_street>

    number = models.CharField(blank=True, max_length=10) # <num>

    apartment_building = models.CharField(blank=True, max_length=10) # <bl>
    entrance = models.CharField(blank=True, max_length=10)  # <vh>
    floor = models.CharField(blank=True, max_length=10)     # <et>
    apartment = models.CharField(blank=True, max_length=10) # <ap>
    other = models.CharField(blank=True, max_length=255)    # <other>

    def __str__(self):
        return self.name
