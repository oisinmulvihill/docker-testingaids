# -*- coding: utf-8 -*-
"""
"""
from docker import Client
from evasion.common import net


def allocate_ports_for(ports):
    """Go through the list of port dicts and add an export_port field with a
    free port which could be used.

    :param ports: a list of dicts.

    The dict is modified in place with the export_port added to it.

    :returns: None

    """
    in_use = []
    for item in ports:
        item['export_port'] = net.get_free_port(exclude_ports=in_use)


def docker_client(config):
    """Return a docker client for the given configuration.
    """
    base_url = config['config']['docker']['base_url']
    return Client(base_url=base_url)
