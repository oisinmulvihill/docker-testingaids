# -*- coding: utf-8 -*-
"""
"""
import os
import time
import uuid
import logging

from testing.aid.dockerbase import DockerBase


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


class DKElasticSearch(DockerBase):
    """This overrides implements the waitForReady needed to make sure
    elasticsearch is ready for use.

    """
    def __init__(self, cfg):
        """Recover our set up from the influxdb container section.
        """
        super(DKElasticSearch, self).__init__(
            cfg, 'elasticsearch', retries=120
        )
        log = get_log("DKElasticSearch")
        self.use_env = False
        self.base_uri = None

        if (
            os.environ.get("ELASTICSEARCH_PORT_9200_TCP_ADDR")
            and
            os.environ.get("ELASTICSEARCH_PORT_9200_TCP_PORT")
        ):
            self.host = os.environ.get("ELASTICSEARCH_PORT_9200_TCP_ADDR")
            self.port = os.environ.get("ELASTICSEARCH_PORT_9200_TCP_PORT")
            log.info(
                (
                    "Using from env ELASTICSEARCH_PORT_9200_TCP_ADDR={} "
                    "and ELASTICSEARCH_PORT_9200_TCP_PORT={}"
                ).format(
                    self.host, self.port
                )
            )
            # Indicate not to start a container but to connect to an
            # exiting instance.
            self.use_env = True

    def setUp(self):
        log = get_log("DKElasticSearch.setUp")

        if self.use_env is False:
            super(DKElasticSearch, self).setUp()

        else:
            log.warn(
                (
                    "Not starting a container. Using an existing running"
                    "ElasticSearch Container on host '{}' and port '{}'"
                ).format(
                    self.host,
                    self.port,
                )
            )

    def tearDown(self):
        log = get_log("DKElasticSearch.tearDown")

        if self.use_env is False:
            super(DKElasticSearch, self).tearDown()

        else:
            log.warn(
                (
                    "Not stopping a container as I'm using an existing running"
                    "ElasticSearch Container on host '{}' and port '{}'"
                ).format(
                    self.host,
                    self.port,
                )
            )

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKElasticSearch.waitForReady")

        log.info("Testing container is ready for use.")

        # wait for the first port to respond to connections:
        if self.use_env is False:
            # wait for the first port to respond to connections:
            self.host = self.settings['interface']
            name = self.settings['export']['wait_for_port']
            ports = self.settings['export']['ports']
            port = [p['export_port'] for p in ports if p['name'] == name]
            self.port = port[0]

        # Connect and then try to create and delete an index. If this works
        # we are ready to roll.
        from elasticsearch import ConnectionError
        from elasticsearch import Elasticsearch as ElasticSearch

        count_down = self.retries
        while True:
            try:
                base_uri = 'http://{}:{}/'.format(self.host, self.port)
                log.info("ElasticSearch base_uri: '{}'".format(base_uri))
                es = ElasticSearch([base_uri])
                idx = "testreadytorolldb_{}".format(uuid.uuid4().hex)
                es.indices.create(index=idx, ignore=400)
                es.indices.delete(index=idx, ignore=[400, 404])

            except ConnectionError:
                log.warn("Connection to DB failed. Retrying...")
                time.sleep(self.sleep_period)
                count_down -= 1
                if not count_down:
                    # Give up:
                    raise

            except:
                # Raise any other exception.
                log.exception("error: ")
                raise

            else:
                # Success done:
                self.base_uri = base_uri
                break
