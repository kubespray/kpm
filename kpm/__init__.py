# -*- coding: utf-8 -*-
__author__ = 'Antoine Legrand'
__email__ = '2t.antoine@gmail.com'
__version__ = '0.25.0'


def version(registry_host=None):
    import requests
    from kpm.registry import Registry
    api_version = None
    ctl_version = __version__
    try:
        registry = Registry(registry_host)
        response = registry.version()
        api_version = response
    except requests.exceptions.RequestException:
        api_version = ".. Connection error"

    return {'api-version': api_version, "client-version": ctl_version}
