# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'eecont.views',

    url(r'^cities/$', 'city_list', name='eecont-city-list-jsonp'),
    url(r'^quarters/$', 'quarter_list', name='eecont-quarter-list-jsonp'),
    url(r'^streets/$', 'street_list', name='eecont-street-list-jsonp'),

)
