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


class DKRethinkDB(DockerBase):
    """This overrides implements the waitForReady needed to make sure rethinkdb
    is ready for use.

    If RETHINKDB_PORT_28015_TCP_ADDR and RETHINKDB_PORT_28015_TCP_PORT are
    defined in the environment, they will be used and no container started.
    This allows test runs which link to containers started and managed
    elsewhere.

    dk_config.yaml entry::

        rethinkdb:
            image: rethinkdb
            interface: 0.0.0.0
            auth:
                user:
                password:
            entrypoint:
            export:
                wait_for_port: db
                ports:
                    - port: 8080
                      name: admin
                    - port: 28015
                      name: db

    """
    def __init__(self, cfg):
        """Recover our set up from the influxdb container section.
        """
        super(DKRethinkDB, self).__init__(cfg, 'rethinkdb')
        log = get_log("DKRethinkDB.__init__")
        self.use_env = False

        if (
            os.environ.get("RETHINKDB_PORT_28015_TCP_ADDR")
            and
            os.environ.get("RETHINKDB_PORT_28015_TCP_PORT")
        ):
            self.host = os.environ.get("RETHINKDB_PORT_28015_TCP_ADDR")
            self.port = os.environ.get("RETHINKDB_PORT_28015_TCP_PORT")
            log.info(
                (
                    "Using from environment RETHINKDB_PORT_28015_TCP_ADDR={} "
                    "and RETHINKDB_PORT_28015_TCP_PORT={}"
                ).format(
                    self.host, self.port
                )
            )
            # Indicate not to start a container but to connect to an
            # exiting instance.
            self.use_env = True

    def setUp(self):
        log = get_log("DKRethinkDB.setUp")

        if self.use_env is False:
            super(DKRethinkDB, self).setUp()

        else:
            log.warn(
                (
                    "Not starting a container. Using an existing running"
                    "RethinkDB on host '{}' and port '{}'"
                ).format(
                    self.host,
                    self.port,
                )
            )

    def tearDown(self):
        log = get_log("DKRethinkDB.tearDown")

        if self.use_env is False:
            super(DKRethinkDB, self).tearDown()

        else:
            log.warn(
                (
                    "Not stopping a container as I'm using an existing running"
                    "RethinkDB on host '{}' and port '{}'"
                ).format(
                    self.host,
                    self.port,
                )
            )

    def waitForReady(self):
        """Wait for the client socker to be available then attempt to create
        and destroy a dummy database.

        """
        log = get_log("DKRethinkDB.waitForReady")

        log.info("Testing container is ready for use.")
        db = "testreadytorolldb_{}".format(uuid.uuid4().hex)

        # wait for the first port to respond to connections:
        if self.use_env is False:
            interface = self.settings['interface']
            name = self.settings['export']['wait_for_port']
            ports = self.settings['export']['ports']
            port = [p['export_port'] for p in ports if p['name'] == name]
            port = port[0]

        else:
            interface = self.host
            port = self.port

        # Create a database then drop it which should test influxdb is running
        # and ready. This may fail with ConnectionError as the container is
        # still in the process of starting influxdb.
        import socket
        import rethinkdb
        from rethinkdb import RqlDriverError

        count_down = self.retries
        while True:
            try:
                conn = rethinkdb.connect(host=interface, port=port, db=db)
                rethinkdb.db_create(db).run(conn)

            except (socket.error, RqlDriverError), err:
                log.warn(
                    "Connection to DB failed. Retrying... Error: {}".format(
                        err
                    )
                )
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
                # Update these now they are confirmed working:
                self.host = interface
                self.port = port
                rethinkdb.db_drop(db).run(conn)
                break
