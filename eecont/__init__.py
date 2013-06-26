# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import Sequence
import copy

from django.utils import six
from django.conf import settings

from bgaddr import parse_address
import remoteecont


###########
# Helpers #
###########

def _client():
    parcel_url  = settings.EECONT['login']['parcel_url']
    password    = settings.EECONT['login']['password']
    service_url = settings.EECONT['login']['service_url']
    username    = settings.EECONT['login']['username']
    econt = remoteecont.RemoteEcontXml(
        service_url, parcel_url, username, password, remoteecont.CurlTransfer)
    return econt


def _dict_get(d, *args):
    try:
        for k in args:
            d = d[k]
        return d
    except (KeyError, TypeError):
        # TODO: log
        return None


def _loadings(address, shipment, services=None):
    """Prepare the loadings request parameter.

    """
    if not isinstance(shipment, Sequence):
        shipment = [shipment]

    if not isinstance(address, Sequence):
        address = [address]

    if services is None:
        services = [{}]
    elif not isinstance(services, Sequence):
        services = [services]

    ret = []
    for address_dict, shipment_dict, services_dict in zip(
            address, shipment, services):

        # TODO: Some properties are copied twice...
        data = copy.deepcopy(settings.EECONT['loading'])

        data['receiver'].update(_receiver(**address_dict))
        data['shipment'].update(_shipment(**shipment_dict))
        data['services'].update(_services(**services_dict))
        ret.append(data)
    return ret


def _receiver(**kwargs):
    """Prepare a dict that represents the `receiver` section of the
    shipment request.

    """
    # Transform arguments
    kwargs['phone_num'] = kwargs.pop('phone_number', '')
    kwargs['name_person'] = kwargs.get('name', '')
    address = kwargs.pop('address', '')
    if isinstance(address, six.string_types):
        other = address
        address = parse_address(address)
        address['street_other'] = other

    # Prepare receiver struct
    ret = copy.deepcopy(settings.EECONT['loading']['receiver'])
    ret.update(kwargs)
    ret.update({
        'street'           : address.get('street', ''),
        'street_num'       : address.get('num', ''),
        'street_bl'        : address.get('ab', ''),
        'street_vh'        : address.get('en', ''),
        'street_et'        : address.get('fl', ''),
        'street_ap'        : address.get('ap', ''),
        'street_other'     : address.get('street_other', ''),
    })
    return ret


def _services(**kwargs):
    """Return a dict that describes the `services` part of the EECONT
    request.

    Arguments:

    - `payment`: This argument represents the payment received from
      the client at the moment of delivery (in the case of pay on
      delivery).  The argument needs to be an integer in coins, for
      example 10 Bulgarian leva will be represented as 1000 because
      1000 Bulgarian stotinki are 10 Bulgarian leva.

    """
    services = copy.deepcopy(settings.EECONT['loading']['services'])

    payment = int(kwargs.get('payment', 0))
    payment = '{}.{}'.format(payment // 100, payment % 100)
    services['cd']['__content__'] = payment
    return services


def _shipment(**kwargs):
    """Return a dict object describes a shipment item as per the
    requirements of the eecont API.

    Arguments:
    - `description`
    - `weight`

    """
    shipment = copy.deepcopy(settings.EECONT['loading']['shipment'])
    shipment.update(kwargs)
    return shipment


def _system(**kwargs):
    """Compile a system dictionary useful as a system parameter on
    request.

    Args:
    response_type
    only_calculate
    validate

    """
    ret = copy.deepcopy(settings.EECONT['system'])
    ret.update(**kwargs)
    return ret


###########
# Request #
###########

def _generic_request(address, shipment, services=None, system=None):
    loadings = _loadings(address, shipment, services)
    system = _system(**(system or {}))
    response = _client().shipping(loadings, system)
    return response


def shipment_request(address, shipment, services):
    system = {'only_calculate': 0, 'validate': 0}
    response = _generic_request(address, shipment, services, system)
    return response


def delivery_info(address, shipment, services):
    system = {'only_calculate': 1, 'validate': 0}
    response = _generic_request(address, shipment, services, system)

    cost = _dict_get(response, 'result', 'e', 'loading_price', 'total')
    try:
        cost = int(round(float(cost) * 100)) # python2 needs int()
    except (TypeError, ValueError):
        pass

    d = _dict_get(response, 'result', 'e', 'delivery_date')
    if d:
        # TODO: convert to python date
        pass

    cost = cost or settings.EECONT['defaults'].get('delivery_cost')
    d = d or settings.EECONT['defaults'].get('delivery_date')
    return {
        'cost': cost,
        'date': d,
    }


def validate_address(address):
    """Return None on successful check or an error string (in Bulgarian)
    in case of any validation error.

    """
    shipment = {
        'description': 'A dummy package',
        'weight': '1',
    }
    services = {
        'payment': 100
    }
    system = {
        'only_calculate': 1,
    }
    response = _generic_request(address, shipment, services, system)
    return _dict_get(response, 'result', 'e', 'error')
