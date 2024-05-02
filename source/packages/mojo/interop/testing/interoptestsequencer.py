"""
.. module:: interoptestsequencer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`InteropTestSequencer` type which is use to control
        the flow of the automation environment startup and test execution sequence for a distributed
        automation environment.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import List,Sequence

import collections
import json
import os
import sys

from mojo.xmods.injection.coupling.integrationcoupling import IntegrationCoupling
from mojo.xmods.markers import MetaFilter

from mojo.landscaping.landscape import Landscape

from mojo.runtime.paths import get_path_for_output

from mojo.testplus.sequencing.testsequencer import TestSequencer

class InteropTestSequencer(TestSequencer):
    """
        The :class:`InteropTestSequencer` is a state machine that helps to orchestrate the flow fo the test run.  It ensures
        that the steps of the test flow are consistent between runs.
    """

    def __init__(self, jobtitle: str, root: str, includes: Sequence[str], excludes: Sequence[str], metafilters: List[MetaFilter]):
        """
            Creates a 'TestSequencer' object which is used to discover the tests and control the flow of a test run.

            :param jobtitle: The name of the test job.
            :param root: The path to the root folder that is the base of the tests.
            :param includes: List of expressions used to determine which tests to include.
                             (scope):(package).(package)@(module)#(testname)
            :param excludes: List of expressions used to determine which tests to exclued from the included tests.
            :param metafilters: List of expressions used to filter tests by metadata
        """
        super().__init__(jobtitle=jobtitle, root=root, includes=includes, excludes=excludes, metafilters=metafilters)

        self._landscape = None
        return

    def attach_to_framework(self, landscape: Landscape):
        """
            Goes through all the integrations and provides them with an opportunity to
            attach to the test environment.
        """

        self._landscape = landscape

        integ_type: IntegrationCoupling

        for _, integ_type in self._integrations.items():
            integ_type.attach_to_framework(landscape=landscape)

        return

    def attach_to_environment(self, landscape):
        """
            Goes through all the integrations and provides them with an opportunity to
            attach to the test environment.
        """

        results_dir = get_path_for_output()

        environment_dict = self.create_password_masked_environment()

        package_dict = collections.OrderedDict()

        package_names = [k for k in sys.modules.keys()]
        package_names.sort()
        for pname in package_names:
            nxtmod = sys.modules[pname]
            if pname.find(".") == -1 and hasattr(nxtmod, "__file__"):
                package_dict[pname] = nxtmod.__file__

        startup_dict = collections.OrderedDict([
            ("command", " ".join(sys.argv)),
            ("environment", environment_dict),
            ("packages", package_dict)
        ])

        startup_full = os.path.join(results_dir, "startup-configuration.json")
        with open(startup_full, 'w') as suf:
            json.dump(startup_dict, suf, indent=True)

        integ_type: IntegrationCoupling

        for _, integ_type in self._integrations.items():
            integ_type.attach_to_environment(landscape)

        return
