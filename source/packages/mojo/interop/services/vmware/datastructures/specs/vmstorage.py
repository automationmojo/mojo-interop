"""
.. module:: vmstorage
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VmStorage*Spec related objects used in the creation of VM(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

from dataclasses import dataclass

@dataclass
class VmStoragePolicySpec:
    policy: str