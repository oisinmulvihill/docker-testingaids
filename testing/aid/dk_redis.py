# -*- coding: utf-8 -*-
"""
"""
import time
import uuid
import logging

import requests

from testing.aid.dockerbase import DockerBase


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


class DKRedis(DockerBase):
    """This overrides implements the waitForReady needed to make sure redis
    is ready for use.

    """
    def __init__(self, cfg):
        """Recover our set up from the redis container section.
        """
        super(DKRedis, self).__init__(cfg, 'redis')

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKRedis.waitForReady")

        # wait for the first port to respond to connections:
        interface = self.settings['interface']
        name = self.settings['export']['wait_for_port']
        # The DB number to check redis is work with:
        db = int(self.settings['export']['db'])
        ports = self.settings['export']['ports']
        port = [p['export_port'] for p in ports if p['name'] == name]
        port = port[0]

        log.info("Testing container is ready for use.")
        value = "testreadytorolldb_{}".format(uuid.uuid4().hex)

        import redis
        from redis.exceptions import ConnectionError

        # Create a database then drop it which should test redis is running
        # and ready. This may fail with ConnectionError as the container is
        # still in the process of starting redis.
        key = 'pnc:redis:check'
        count_down = self.retries
        while True:
            try:
                conn = redis.StrictRedis(host=interface, port=port, db=db)
                conn.set(key, value)
                val = conn.get(key)
                if val == value:
                    break

            except ConnectionError:
                log.warn("Redis not ready. Retrying...")

            except:
                # Raise any other exception.
                log.exception("error: ")

                log.warn("Connection to Redis failed. Retrying...")
                time.sleep(self.sleep_period)
                count_down -= 1
                if not count_down:
                    # Give up:
                    raise

            else:
                conn.delete(key)
                break
