# -*- coding: utf-8 -*-
"""
"""
import time
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
        super(DKElasticSearch, self).__init__(cfg, 'elasticsearch')

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

        # Create a database then drop it which should test influxdb is running
        # and ready. This may fail with ConnectionError as the container is
        # still in the process of starting influxdb.
        import socket
        from pyelasticsearch import ElasticSearch

        count_down = self.retries
        while True:
            try:
                base_uri = 'http://{}:{}'.format(interface, port)
                log.info("ElasticSearch base_uri: '{}'".format(base_uri))
                conn = ElasticSearch(base_uri)
                #conn.delete_all_indexes()
                break

            except socket.error:
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
