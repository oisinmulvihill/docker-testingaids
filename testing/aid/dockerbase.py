# -*- coding: utf-8 -*-
"""
"""
import logging

from evasion.common import net

from testing.aid.tools import docker_client
from testing.aid.tools import allocate_ports_for


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


class DockerBase(object):

    def __init__(self, cfg, config_entry, retries=60, sleep_period=2):
        """
        """
        log = get_log("DockerBase.__init__")
        self.cfg = cfg
        entry = self.cfg['config']['containers'][config_entry]
        allocate_ports_for(entry['export']['ports'])
        self.entrypoint = entry.get('entrypoint')
        self.settings = entry
        self.ports = [p['port'] for p in self.settings['export']['ports']]
        self.conn = docker_client(self.cfg)
        self.containerId = None
        self.retries = retries
        self.sleep_period = sleep_period
        log.debug("settings: '{}'".format(self.settings))

    def waitForReady(self):
        """Called at the end of setUp to allow the end user to indicate the
        container is ready for use.

        The base class peforms no actions. The end user should override and
        implement some connection checking. The wait and return when ready or
        raise some kind of timeout exception.

        """

    def setUp(self):
        """Create the container and start the container it ready for testing.
        """
        log = get_log("DockerBase.setUp")

        kwargs = {}
        if self.entrypoint:
            kwargs['entrypoint'] = self.entrypoint

        box = self.conn.create_container(
            image=self.settings['image'],
            detach=True,
            ports=self.ports,
            **kwargs
        )
        log.debug("box: '{}'".format(box))
        self.containerId = box['Id']

        port_bindings = {}
        interface = self.settings['interface']
        for entry in self.settings['export']['ports']:
            port_bindings[entry['port']] = (
                interface, entry['export_port']
            )
        log.debug("box: port binding '{}'".format(port_bindings))

        self.conn.start(
            self.containerId,
            port_bindings=port_bindings,
        )
        log.debug(
            "box: container started '{}'".format(self.settings['image'])
        )

        result = self.conn.inspect_container(self.containerId)
        if not result['State']['Running']:
            raise SystemError(
                "Container failed to start '{}:{}'".format(
                    self.settings['image'],
                    self.containerId
                )
            )

        log.info(
            "Container to running '{}:{}'. Checking it is ready...".format(
                self.settings['image'],
                self.containerId
            )
        )

        # wait for the first port to respond to connections:
        interface = self.settings['interface']
        name = self.settings['export']['wait_for_port']
        ports = self.settings['export']['ports']
        port = [p['export_port'] for p in ports if p['name'] == name]
        port = port[0]

        is_ready = net.wait_for_service(interface, port, retries=self.retries)
        if not is_ready:
            log.error()
            raise SystemError()

        self.waitForReady()

        log.info(
            "Container is ready for use '{}:{}'".format(
                self.settings['image'],
                self.containerId
            )
        )

    def tearDown(self):
        """Stop and remove the running docker instance setUp started.
        """
        log = get_log("DKInfluxDB.tearDown")

        log.info(
            "Stopping container '{}:{}'".format(
                self.settings['image'],
                self.containerId
            )
        )
        self.conn.kill(self.containerId)

        result = self.conn.inspect_container(self.containerId)
        if result['State']['Running']:
            log.error(
                "Container failed to stop '{}:{}'".format(
                    self.settings['image'],
                    self.containerId
                )
            )

        self.conn.remove_container(self.containerId, force=True)
