"""
.. module:: poweragents
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerAgent object instances used to communicate with power controllers.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


import weakref


class DliPowerAgent:

    def __init__(self, interface, attachment):
        self._interface = interface
        self._attachment = attachment
        return

    def on(self):
        success = self._interface.on(outlet=self._attachment)
        return success

    def off(self):
        success = self._interface.off(outlet=self._attachment)
        return success
