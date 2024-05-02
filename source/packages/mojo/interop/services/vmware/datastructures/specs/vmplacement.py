"""
.. module:: vmplacementspec
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmPlacementSpec object used to indicate the placement of a newly created VM.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

from typing import Optional

from dataclasses import dataclass

@dataclass
class VmPlacementSpec:
    datastore: str
    folder: str
    cluster: Optional[str] = None
    host: Optional[str] = None
    resource_pool: Optional[str] = None
