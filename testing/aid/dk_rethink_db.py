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


class DKRethinkDB(DockerBase):
    """This overrides implements the waitForReady needed to make sure rethinkdb
    is ready for use.

    """
    def __init__(self, cfg):
        """Recover our set up from the influxdb container section.
        """
        super(DKRethinkDB, self).__init__(cfg, 'rethinkdb')

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKRethinkDB.waitForReady")

        log.info("Testing container is ready for use.")
        db = "testreadytorolldb_{}".format(uuid.uuid4().hex)

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
        import rethinkdb

        count_down = self.retries
        while True:
            try:
                conn = rethinkdb.connect(host=interface, port=port, db=db)
                rethinkdb.db_create(db).run(conn)

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

            else:
                rethinkdb.db_drop(db).run(conn)
                break
