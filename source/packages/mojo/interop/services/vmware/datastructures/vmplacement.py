"""
.. module:: vmplacementspec
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmPlacementSpec object used to indicate the placement of a newly created VM.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

from typing import Optional

class VmPlacementSpec(dataclass):
    datastore: str
    folder: str
    cluster: Optional[str] = None
    host: Optional[str] = None
    resource_pool: Optional[str] = None
