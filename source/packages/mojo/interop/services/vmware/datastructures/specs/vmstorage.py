"""
.. module:: vmstorage
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VmStorage*Spec related objects used in the creation of VM(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

from dataclasses import dataclass

@dataclass
class VmStoragePolicySpec:
    policy: str