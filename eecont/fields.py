# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import collections
import functools

from django.core import exceptions
from django.db import models
from django.utils import six


class OfficeListField(six.with_metaclass(models.SubfieldBase, models.Field)):

    description = 'Hold a list of Econt office codes'

    # E1002: Use super on an old style class Used when an old style
    # class use the super builtin.
    # pylint: disable=E1002
    def __init__(self, *args, **kwargs):
        super(OfficeListField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def get_prep_value(self, value):
        return ','.join([str(i) for i in value])

    def to_python(self, value):
        if isinstance(value, six.string_types):
            try:
                return [int(x) for x in value.split(',') if len(x.strip())]
            except ValueError as e:
                raise exceptions.ValidationError(str(e))

        elif isinstance(value, list):
            try:
                return [int(x) for x in value]
            except ValueError:
                msg = 'All items should be ints (or int strings): {}'.\
                    format(value)
                raise exceptions.ValidationError(msg)

        else:
            msg = 'Pass string or list of integers, not {}'.format(type(value))
            raise exceptions.ValidationError(msg)

# TODO: widget?
class WeekDaysField(six.with_metaclass(models.SubfieldBase, models.Field)):

    description = 'Field that holds a boolean value for each day of the week'

    M_DAYS = [0x01,             # Monday
              0x02,             # Tuesday
              0x04,             # Wednesday
              0x08,             # Thursday
              0x10,             # Friday
              0x20,             # Saturday
              0x40]             # Sunday   

    # pylint: disable=E1002
    def __init__(self, *args, **kwargs):
        super(WeekDaysField, self).__init__(*args, **kwargs)

    def _itob(self, i):
        return True if i >= 1 else False

    def get_internal_type(self):
        return 'PositiveIntegerField'

    def get_prep_value(self, value):
        """
        Convert lists to their respective int values.  For example
        [True, True, True, False, False, True, True]
        is converted to
        0b1100111 or 103
        """
        v = functools.reduce(lambda a, b: 2*a + (1 if b else 0), value, 0)
        # now reverse bits of v
        return int('{:07b}'.format(v)[::-1], 2)

    def to_python(self, value):
        if isinstance(value, six.string_types):
            if not value:
                value = '0'

            try:
                if value.startswith('0b'):
                    value = int(value, 2)
                else:
                    value = int(value)
            except ValueError as e:
                raise exceptions.ValidationError(str(e))

        if isinstance(value, int):
            return [self._itob(value & mask) for mask in self.M_DAYS]

        elif isinstance(value, collections.Sequence):
            # value is a list or tuple
            if not all([isinstance(x, bool) for x in value]):
                msg = 'All items should be boolean: {}'.format(value)
                raise exceptions.ValidationError(msg)
            return value

        else:
            msg = 'Pass string or list of boolean, not {}'.format(type(value))
            raise exceptions.ValidationError(msg)
