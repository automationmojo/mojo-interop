"""
.. module:: interoptestjob
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the :class:`InteropTestJob` class which is utilized for each test
               run as the parent container for all test results.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import List, Optional

from mojo.landscaping.wellknown import LandscapeSingleton

from mojo.testplus.sequencing.testsequencer import TestSequencer
from mojo.testplus.testjob import TestJob

from mojo.interop.testing.interoptestsequencer import InteropTestSequencer


class InteropTestJob(TestJob):
    """
        The :class:`TestJob` spans the execution of all :class:`TestPack` and organizes the
        flow of execution of test packs.  It allows for the sequencing of the execution of test
        packs so as to optimize the time test runs spend performing setup and tearnown tasks.  This
        allows for the optimization of infrastructure resources.

        * Single Instance
        * Setup Test Landscape
        * Jobs have an expected number of tests based
        * Collects and organizes results from all the :class:`TestPack` runs

        * Can be used to customize the sequencing of :class:`TestPack` runs.
    """


    def __init__(self, logger, testroot, includes: Optional[List[str]]=None, excludes: Optional[List[str]]=None,
                 metafilters: Optional[List[str]]=None, test_module: Optional[str]=None, parser=None):
        """
            Constructor for a :class:`TestJob`.  It initializes the member variables based on the parameters passed
            from the entry point function and the class member data declared on :class:`TestJob` derived classes.
        """
        super().__init__(logger=logger, testroot=testroot, includes=includes, excludes=excludes,
                      metafilters=metafilters, test_module=test_module, parser=parser)

        return

    def fire_activate_configuration(self):

        landscape = LandscapeSingleton()

        landscape.activate_configuration()

        return


    def fire_activate_integration(self):

        landscape = LandscapeSingleton()

        landscape.activate_integration()
        
        return


    def fire_activate_operations(self):

        landscape = LandscapeSingleton()

        landscape.activate_operations()
        
        return


    def fire_attach_to_environment(self, tseq: TestSequencer):
        
        landscape = LandscapeSingleton()

        tseq.attach_to_environment(landscape=landscape)
        
        return


    def fire_attach_to_framework(self, tseq: TestSequencer):
        
        landscape = LandscapeSingleton()

        tseq.attach_to_framework(landscape=landscape)

        return


    def _create_sequencer(self):
        """
            Simple hook function to make it possible to overload the type of the TestSequencer that is created
            for jobs.
        """
        inst = InteropTestSequencer(jobtitle=self.title, root=self._testroot, includes=self.includes, excludes=self.excludes, metafilters=self.metafilters)
        return inst


class DefaultTestJob(InteropTestJob):
    """
        The :class:`DefautTestJob` is utilized as a job container when a job was not specified.
    """
    name = "Test Job"
    description = "Unspecified test job."
