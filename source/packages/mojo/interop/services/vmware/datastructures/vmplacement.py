"""
.. module:: vmplacementspec
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmPlacementSpec object used to indicate the placement of a newly created VM.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

from typing import Optional

from dataclasses import dataclass

@dataclass
class VmPlacementSpec:
    datastore: str
    folder: str
    cluster: Optional[str]
    host: Optional[str]
    resource_pool: Optional[str]
