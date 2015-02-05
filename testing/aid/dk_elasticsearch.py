# -*- coding: utf-8 -*-
"""
"""
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
        super(DKElasticSearch, self).__init__(cfg, 'elasticsearch', retries=20)

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKElasticSearch.waitForReady")

        log.info("Testing container is ready for use.")

        # wait for the first port to respond to connections:
        interface = self.settings['interface']
        name = self.settings['export']['wait_for_port']
        ports = self.settings['export']['ports']
        port = [p['export_port'] for p in ports if p['name'] == name]
        port = port[0]

        # Connect and then try to create and delete an index. If this works
        # we are ready to roll.
        from elasticsearch import ConnectionError
        from elasticsearch import Elasticsearch as ElasticSearch

        count_down = self.retries
        while True:
            try:
                base_uri = 'http://{}:{}/'.format(interface, port)
                log.info("ElasticSearch base_uri: '{}'".format(base_uri))
                es = ElasticSearch([base_uri])
                idx = "testreadytorolldb_{}".format(uuid.uuid4().hex)
                es.indices.create(index=idx, ignore=400)
                es.indices.delete(index=idx, ignore=[400, 404])
                break

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
