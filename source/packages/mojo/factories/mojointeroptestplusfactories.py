"""
.. module:: mojointerotestplusfactories
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the factories for extending the TestPlus package to
               support included landscaping and interop protocols.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Type

from mojo.extension.extensionfactory import ExtFactory

from mojo.testplus.extensionprotocols import TestPlusExtensionProtocol
from mojo.testplus.testjob import TestJob

from mojo.interop.testing.interoptestjob import InteropTestJob

class MojoInteropTestPlusExtentionFactory(ExtFactory, TestPlusExtensionProtocol):

    PRECEDENCE = 10

    def get_testplus_default_job_type() -> Type[TestJob]:
        """
            Used to lookup and return the most relevant default job type as determined
            by the super factory search path.
        """
        return InteropTestJob