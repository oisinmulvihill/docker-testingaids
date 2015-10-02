# -*- coding: utf-8 -*-
"""
"""
import logging

import pytest


class WebDriver(object):

    def __init__(self, config={}):
        """
        """
        self.log = logging.getLogger("{0}.{1}".format(__name__, "WebDriver"))
        # Import only if its used:
        from pyvirtualdisplay import Display
        from selenium import webdriver

        self.display_size = config.get('display_size', (1024, 768))
        self.log.debug("Test display size: {}".format(self.display_size))
        self.visible = config.get('display_visible', 0)
        msg = "display visible? {}"
        msg = msg.format("Yes") if self.visible else "No"
        self.log.debug("Show test display: {}".format(msg))
        self.display = Display(visible=self.visible, size=self.display_size)

        self.driver = webdriver.Firefox()
        self.log.debug("Using web driver: Firefox")

    def start(self):
        """Start the display ready for webdriver to use.
        """
        self.display.start()

    def stop(self):
        """Stop the display and webdriver.
        """
        self.driver.close()
        self.display.stop()


@pytest.fixture(scope='session')
def webdriver(request):
    """Return the WebDriver instance to control the browser with.

    The stop() will be called on tear down.

    """
    service = WebDriver()

    service.start()
    request.addfinalizer(service.stop)

    return service.driver
