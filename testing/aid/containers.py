# -*- coding: utf-8 -*-
"""
"""
import logging
import os.path

import yaml
import pytest

from testing.aid.dk_redis import DKRedis
from testing.aid.dk_influx_db import DKInfluxDB
from testing.aid.dk_rethink_db import DKRethinkDB
from testing.aid.dk_elasticsearch import DKElasticSearch


@pytest.fixture(scope='session')
def dk_logger():
    """
    """
    class DKLogger(object):

        def __init__(self):
            log = logging.getLogger()
            hdlr = logging.StreamHandler()
            fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
            formatter = logging.Formatter(fmt)
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.DEBUG)
            log.propagate = False

        def get_log(self, e=None):
            return logging.getLogger(
                "{0}.{1}".format(__name__, e) if e else __name__
            )

    log = DKLogger()
    log.get_log().info("dk_logger: active and ready to roll.")

    return log


@pytest.fixture(scope='session')
def dk_config(request):
    """
    """
    log = request.getfuncargvalue('dk_logger').get_log('dk_config')

    home_dir = os.path.abspath(os.path.expanduser("~"))
    log.debug("home_dir: '{}'".format(home_dir))

    config_file = os.environ.get("DK_CONFIG_FILE")
    if config_file:
        config_file = os.path.abspath(os.path.expanduser(config_file))
    else:
        config_file = os.path.join(home_dir, 'dk_config.ini')

    if not os.path.isfile(config_file):
        raise SystemError(
            "Error: configuration file '{}' not found!".format(config_file)
        )

    log.info("config_file: '{}'".format(config_file))
    with open(config_file, "r") as fd:
        config = yaml.load(fd.read())

    return dict(
        home_dir=home_dir,
        config=config,
    )


@pytest.fixture(scope='session')
def dk_influxdb(request):
    """Create an influxdb container ready for testing.

    This depends on the dk_config fixture.

    :returns: An instance of DKInfluxDB.

    The instance variable settings is a dict with all the connection details
    the end user needs to connect.

    The end user does not need to worry about stopping the container as this
    will be handled automatically. The container is killed and removed when
    the test run finishes.

    """
    dk_cfg = request.getfuncargvalue('dk_config')

    service = DKInfluxDB(dk_cfg)
    service.setUp()
    request.addfinalizer(service.tearDown)

    return service


@pytest.fixture(scope='function')
def dk_rethinkdb(request):
    """Create an RethinkDB container ready for testing.

    This depends on the dk_config fixture.

    :returns: An instance of DKRethinkDB.

    The instance variable settings is a dict with all the connection details
    the end user needs to connect.

    The end user does not need to worry about stopping the container as this
    will be handled automatically. The container is killed and removed when
    the test run finishes.

    """
    dk_cfg = request.getfuncargvalue('dk_config')

    service = DKRethinkDB(dk_cfg)
    service.setUp()
    request.addfinalizer(service.tearDown)

    return service


@pytest.fixture(scope='function')
def dk_redis(request):
    """Create an Redis container ready for testing.

    This depends on the dk_config fixture.

    :returns: An instance of DKRedis.

    The instance variable settings is a dict with all the connection details
    the end user needs to connect.

    The end user does not need to worry about stopping the container as this
    will be handled automatically. The container is killed and removed when
    the test run finishes.

    """
    dk_cfg = request.getfuncargvalue('dk_config')

    service = DKRedis(dk_cfg)
    service.setUp()
    request.addfinalizer(service.tearDown)

    return service


@pytest.fixture(scope='function')
def dk_elasticsearch(request):
    """Create an ElasticSearch container ready for testing.

    This depends on the dk_config fixture.

    :returns: An instance of DKElasticSearch.

    """
    dk_cfg = request.getfuncargvalue('dk_config')

    service = DKElasticSearch(dk_cfg)
    service.setUp()
    request.addfinalizer(service.tearDown)

    return service
