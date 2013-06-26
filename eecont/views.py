# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

from django.core import serializers
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import response
from django.views.generic import list as glist

from eecont import models


def json_response(request, serializable):
    cb = request.GET.get('callback', 'callback')

    # if isinstance(serializable, QuerySet):
    #     data = serializers.serialize('json', serializable)
    # else:
    data = json.dumps(list(serializable), ensure_ascii=False)

    content = '{}({});'.format(cb, data)

    resp = response.HttpResponse(content,
        content_type='application/json; charset=utf-8')
    return resp


class BaseJsonpList(glist.BaseListView):

    limit = 10

    def get_queryset(self):
        qs = super(BaseJsonpList, self).get_queryset()
        query = self.request.GET.get('query')
        if query:
            qs = qs.filter(name__istartswith=query)\
                   .values('name')\
                   .annotate(count=Count('name'))[:self.limit]
        return qs

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        # context = self.get_context_data(object_list=self.object_list)
        return json_response(request, self.object_list)


class CityList(BaseJsonpList):
    model = models.City


class QuarterList(BaseJsonpList):
    model = models.Quarter


class StreetList(BaseJsonpList):
    model = models.Street


city_list = CityList.as_view()
quarter_list = QuarterList.as_view()
street_list = StreetList.as_view()
