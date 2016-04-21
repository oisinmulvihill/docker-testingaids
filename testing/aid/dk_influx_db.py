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


class DKInfluxDB(DockerBase):
    """This overrides implements the waitForReady needed to make sure influxdb
    is ready for use.

    """
    def __init__(self, cfg):
        """Recover our set up from the influxdb container section.
        """
        super(DKInfluxDB, self).__init__(cfg, 'influxdb')

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKInfluxDB.waitForReady")

        # wait for the first port to respond to connections:
        interface = self.settings['interface']
        name = self.settings['export']['wait_for_port']
        ports = self.settings['export']['ports']
        port = [p['export_port'] for p in ports if p['name'] == name]
        port = port[0]

        log.info("Testing container is ready for use.")
        db = "testreadytorolldb_{}".format(uuid.uuid4().hex)
        from influxdb import InfluxDBClient
        conn = InfluxDBClient(
            interface,
            int(port),
            self.settings['auth']['user'],
            self.settings['auth']['password'],
            db
        )

        # Create a database then drop it which should test influxdb is running
        # and ready. This may fail with ConnectionError as the container is
        # still in the process of starting influxdb.
        count_down = self.retries
        while True:
            try:
                conn.create_database(db)

            except requests.ConnectionError:
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
                conn.drop_database(db)
                break
