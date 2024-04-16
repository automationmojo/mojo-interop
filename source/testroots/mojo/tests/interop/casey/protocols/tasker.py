

from typing import Generator, List

import os
import tempfile
import time
import zipfile

from mojo import testplus


from mojo.landscaping.landscape import Landscape
from mojo.landscaping.includefilters import IncludeDeviceByDeviceType

from mojo.results.model.taskingresult import TaskingResult

from mojo.interop.clients.linux.linuxclient import LinuxClient

from mojo.interop.protocols.tasker.taskernode import TaskerClientNode
from mojo.interop.protocols.tasker.taskercontroller import ClientTaskerController
from mojo.interop.protocols.tasker.taskingadapter import TaskingAdapter
from mojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise

from mojo.interop.protocols.tasker.examples.helloworldtasking import HelloWorldTasking


from mojo.runtime.paths import get_path_for_output

from mojo.testplus.sequencing.testsequencer import TestSequencer


@testplus.resource()
def create_tasking_adapter(sequencer: TestSequencer, lscape: Landscape, constraints={}) -> Generator[LinuxClient, None, None]:
    
    lcl_output_dir = get_path_for_output()

    lcl_taskings_dir = os.path.join(lcl_output_dir, "taskings")
    lcl_output_basename = os.path.basename(lcl_output_dir)

    rmt_output_dir = os.path.join("~/mjr/results/testresults", lcl_output_basename)
    rmt_tasking_dir = os.path.join("~/mjr/results/testresults", lcl_output_basename, "taskings")

    includes = [IncludeDeviceByDeviceType("network/client-linux")]

    client_list = lscape.get_devices(include_filters=includes)

    tcontroller = ClientTaskerController()

    tcontroller.start_tasker_network(client_list, output_directory=rmt_output_dir)

    tadapter = TaskingAdapter(tcontroller, sequencer)

    yield tadapter

    tcontroller.stop_tasker_network()

    zip_contexts = []

    tasker_nodes = tcontroller.tasker_nodes

    tnode: TaskerClientNode

    for nidx, tnode in enumerate(tasker_nodes):
        zfile = f"tasking-results-{nidx}.zip"
        zip_contexts.append((tnode, zfile))
    
    for tnode, zfile in zip_contexts:
        lcl_archive_file = tempfile.mktemp(suffix=".zip", prefix="taskings-archive-")
        
        archive_basename = os.path.basename(lcl_archive_file)
        rmt_archive_file = tnode.archive_folder(folder_to_archive=rmt_tasking_dir, dest_folder="~/archives", archive_name=archive_basename)

        client: LinuxClient = tnode.client

        client.ssh.file_pull(rmt_archive_file, lcl_archive_file)

        if not os.path.exists(lcl_taskings_dir):
            os.makedirs(lcl_taskings_dir)

        with zipfile.ZipFile(lcl_archive_file, 'r') as zipf:
            zipf.extractall(lcl_taskings_dir)


@testplus.param(create_tasking_adapter, identifier="tadapter")
def test_tasker_say_hello(tadapter: TaskingAdapter):

    with tadapter.create_tasking_group_scope("Hello Group") as hgrp:

        hgrp.execute_tasking(tasking=HelloWorldTasking, message="Hello World", iterations=100)

        time.sleep(5)

        for prom in hgrp.promises:
            prom.call_tasking_method("log_message", "Special Message")

        results: List[TaskingResult] = hgrp.wait_for_tasking_results()
        testplus.verify_tasking_results(results, "The specified taskings did not complete successfully.", hgrp.name)

    return
