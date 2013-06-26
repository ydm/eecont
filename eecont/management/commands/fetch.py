# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management import base
from django.utils import six
from django.utils.six import print_

from eecont import inserter


class Command(base.BaseCommand):

    args = 'hehe'
    help = '''Fetch and store in the database all the information \
needed to make delivery requests with the eEcont API.'''
    
    def handle(self, *args, **kwargs):
        conf = settings.EECONT['login']

        which = map(lambda s: six.text_type(s), args)
        which = map(six.text_type.lower, which)

        a = {'verbosity': int(kwargs['verbosity']),
             'which': which}
        a.update(conf)

        inserter.fetch_and_insert(**a)
