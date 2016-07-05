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


class DKRedis(DockerBase):
    """This overrides implements the waitForReady needed to make sure redis
    is ready for use.

    """
    def __init__(self, cfg):
        """Recover our set up from the redis container section.
        """
        super(DKRedis, self).__init__(cfg, 'redis')
        log = get_log("DKRedis")
        self.use_env = False

        if (
            os.environ.get("REDIS_PORT_6379_TCP_ADDR")
            and
            os.environ.get("REDIS_PORT_6379_TCP_PORT")
        ):
            self.host = os.environ.get("REDIS_PORT_6379_TCP_ADDR")
            self.port = os.environ.get("REDIS_PORT_6379_TCP_PORT")
            log.info(
                (
                    "Using from environment REDIS_PORT_6379_TCP_ADDR={} "
                    "and REDIS_PORT_6379_TCP_PORT={}"
                ).format(
                    self.host, self.port
                )
            )
            # Indicate not to start a container but to connect to an
            # exiting instance.
            self.use_env = True

    def setUp(self):
        log = get_log("DKRedis.setUp")

        if self.use_env is False:
            super(DKRedis, self).setUp()

        else:
            log.warn(
                (
                    "Not starting a container. Using an existing running"
                    "Redis Container on host '{}' and port '{}'"
                ).format(
                    self.host,
                    self.port,
                )
            )

    def tearDown(self):
        log = get_log("DKRedis.tearDown")

        if self.use_env is False:
            super(DKRedis, self).tearDown()

        else:
            log.warn(
                (
                    "Not stopping a container as I'm using an existing running"
                    "Redis Container on host '{}' and port '{}'"
                ).format(
                    self.host,
                    self.port,
                )
            )

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKRedis.waitForReady")

        # wait for the first port to respond to connections:
        if self.use_env is False:
            # wait for the first port to respond to connections:
            self.host = self.settings['interface']
            name = self.settings['export']['wait_for_port']
            # The DB number to check redis is work with:
            db = int(self.settings['export']['db'])
            ports = self.settings['export']['ports']
            port = [p['export_port'] for p in ports if p['name'] == name]
            self.port = port[0]

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
                conn = redis.StrictRedis(host=self.host, port=self.port, db=db)
                conn.set(key, value)
                conn.get(key)

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
                # Done:
                conn.delete(key)
                break
