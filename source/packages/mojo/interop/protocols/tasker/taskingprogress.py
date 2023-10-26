"""
.. module:: taskingprogress
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskingProgress` class which is used to report tasking progress.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"


from dataclasses import dataclass

@dataclass
class TaskingProgress:

    range_min: int
    range_max: int
    position: int
    status: str

    def as_dict(self) -> dict:

        rtnval = {
            "range_min": self.range_min,
            "range_max": self.range_max,
            "position": self.position,
            "status": self.status,
        }

        return rtnval