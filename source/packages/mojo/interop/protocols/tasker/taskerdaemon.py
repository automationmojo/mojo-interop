"""
.. module:: taskerdaemon
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerServerDaemon` class which is a used to create a
               daemonized instance of the TaskerServer.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



import argparse
import atexit
import configparser
import os
import psutil
import signal
import sys
import time
import traceback


from mojo.interop.protocols.tasker.taskerserver import TaskerServer


service_logger = None
svclog_stream = None

SERVICE_LOGGER = "TASKER"


def write_trace(logfile: str, message: str):

    with open(logfile, 'a+') as tf:
        tf.write(message)
        tf.write("\n")

    return

DAEMON_DEBUG_MODE = False


class TaskerServerDaemon(object):

    #Default maximum for the number of available file descriptors
    DEFAULT_MAXFD = 1024

    #Default file mode creation mask for the daemon
    DEFAULT_UMASK = 0

    #Default working directory for the daemon
    DEFAULT_ROOTDIR = "/"

    #Default device null
    DEFAULT_DEVNULL = "/dev/null"

    SERVER_CONFIG_PATH = "/opt/tasker/tasker.conf"
    SERVER_LOGDIR = "/opt/tasker/logs"
    SERVER_PID_FILE = "/var/run/tasker/tasker.pid"


    def __init__(self):
        """
            This is a generic daemon class intended to make it easy to create a daemon.  A daemon has the following configurable
            behaviors:

                1. Resets the current working directory to '/'
                2. Resets the current file creation mode mask to 0
                3. Closes all open files (1024)
                4. Detaches from the starting terminal and redirects standard I/O streams to '/dev/null'

            References:
                1. Advanced Programming in the Unix Environment: W. Richard Stevens
            """
        self._pid_file = self.SERVER_PID_FILE

        if not os.path.exists(self.SERVER_LOGDIR):
            os.makedirs(self.SERVER_LOGDIR)

        self._pre_daemon_logfile = os.path.join(self.SERVER_LOGDIR, "tasker-service-pre-daemon.log")
        self._daemon_logfile = os.path.join(self.SERVER_LOGDIR, "tasker-service-daemon.log")
        self._daemon_error_logfile = os.path.join(self.SERVER_LOGDIR, "tasker-error-daemon.log")

        self._debug_assistant = None
        return


    def daemonize(self):
        """
            This method detaches the current process from the controlling terminal and forks
            it to a process that is a background daemon process.
        """

        write_trace(self._daemon_logfile, "Daemonizing tasker service ...")

        proc_id = None
        try:
            # Fork the 'FIRST' child process and let the parent process where (pid > 0) exit cleanly and return
            # to the terminal
            proc_id = os.fork()
        except OSError as os_err:
            err_msg = "%s\n    errno=%d\n" % (os_err.strerror, os_err.errno)
            write_trace(self._daemon_logfile, err_msg)
            raise Exception (err_msg)

        # Fork returns 0 in the child and a process id in the parent.  If we are running in the parent
        # process then exit cleanly with no error.
        if proc_id > 0:
            sys.exit(0)

        # Call os.setsid() to:
        #    1. Become the session leader of this new session
        #    2. Become the process group leader of this new process group
        #    3. This also guarantees that this process will not have controlling terminal
        os.setsid()

        proc_id = None
        try:
            # For the 'SECOND' child process and let the parent process where (proc_id > 0) exit cleanly
            # This second process fork has the following effects:
            #     1. Since the first child is a session leader without controlling terminal, it is possible
            #        for it to acquire one be opening one in the future.  This second fork guarantees that
            #        the child is no longer a session leader, preventing the daemon from ever acquiring a
            #        controlling terminal.
            proc_id = os.fork()
        except OSError as os_err:
            err_msg = "%s\n    errno=%d\n" % (os_err.strerror, os_err.errno)
            write_trace(self._daemon_logfile, err_msg)
            raise Exception (err_msg)

        # Fork returns 0 in the child and a process id in the parent.  If we are running in the parent
        # process then exit cleanly with no error.
        if proc_id > 0:
            sys.exit(0)

        write_trace(self._daemon_logfile, "Tasker daemon process started...")

        # We want to change the working directory of the daemon to '/' to avoid the issue of not being
        # able to unmount the file system at shutdown time.
        os.chdir(self.DEFAULT_ROOTDIR)

        # We don't want to inherit the file mode creation flags from the parent process.  We
        # give the child process complete control over the permissions
        os.umask(self.DEFAULT_UMASK)

        stdin_fileno = sys.stdin.fileno()
        stdout_fileno = sys.stdout.fileno()
        stderr_fileno = sys.stderr.fileno()

        # Go through all the file descriptors that could have possibly been open and close them
        # This includes the existing stdin, stdout and stderr
        sys.stdout.flush()
        sys.stderr.flush()

        proc = psutil.Process()

        # Close all 1024 possible open FDs
        for _, fd in proc.open_files():
            try:
                os.close(fd)
            except OSError as os_err:
                pass
            except:
                err_trace = traceback.format_exc()
                write_trace(self._daemon_error_logfile, err_trace)

        # Create the standard file descriptors and redirect them to the standard file descriptor
        # numbers 0 stdin, 1 stdout, 2 stderr
        stdin_f = open(self.DEFAULT_DEVNULL , 'r')
        os.dup2(stdin_f.fileno(), stdin_fileno)

        stdout_f = open(self.DEFAULT_DEVNULL, 'a+')
        os.dup2(stdout_f.fileno(), stdout_fileno)

        stderr_f = open(self.DEFAULT_DEVNULL, 'a+')
        os.dup2(stderr_f.fileno(), stderr_fileno)

        write_trace(self._daemon_logfile, "Registering remove_pidfile ...")
        # Register an the removal of the PID file on python interpreter exit
        atexit.register(self._remove_pidfile)

        # Create the pid file to prevent multiple launches of the daemon
        pid_str = str(os.getpid())
        with open(self._pid_file, 'w') as pid_f:
            pid_f.write("%s\n" % pid_str)

        write_trace(self._daemon_logfile, f"Tasker service running as pid={pid_str} ...")

        return


    def process_exists(self, process_id):
        """
            Checks to see if a process exists
        """
        result = None
        try:
            os.kill(process_id, 0)
            result = True
        except OSError:
            result = False
        return result


    def restart(self):
        """
            Restart the Tasker Service
        """
        self.stop()
        self.start()
        return


    def run(self):
        """
            This is the main 'Tasker Service' entry method that will setup the DBUS interfaces
            to handle the Bluetooth integration for the service.
        """
        
        start_debugger = False

        if os.path.exists(self.SERVER_CONFIG_PATH):
            write_trace(self._daemon_logfile, f"Found tasker daemon configuration file ...")
            
            config = configparser.ConfigParser()
            config.read(self.SERVER_CONFIG_PATH)

            write_trace(self._daemon_logfile, f"Processing tasker daemon configuration file ...")

            if "DEFAULT" in config:
                write_trace(self._daemon_logfile, f"Found configuration 'DEFAULT' section ...")
                defsect = config["DEFAULT"]
                if "Debugger" in defsect:
                    dbgval = defsect["Debugger"].strip()
                    if dbgval == "yes":
                        start_debugger = True

        if start_debugger:
            write_trace(self._daemon_logfile, f"Tasker starting debug assistant ...")
            self.run_debug_assistant()

        write_trace(self._daemon_logfile, f"Tasker creating tasker server instance ...")

        logging_directory = os.path.dirname(self._daemon_logfile)

        server = TaskerServer(hostname="0.0.0.0", logging_directory=logging_directory)

        write_trace(self._daemon_logfile, f"Tasker calling tasker server serve_forever ...")
        server.serve_forever()

        return

    def run_debug_assistant(self):

        from mojo.xmods.xdebugger import DebugPyAssistant, PORT_DEBUGPY_ASSISTANT

        endpoint = ("0.0.0.0", PORT_DEBUGPY_ASSISTANT)

        self._debug_assistant = DebugPyAssistant("TaskerRmtDebugger", endpoint=endpoint)

        write_trace(self._daemon_logfile, f"Tasker debug assistant start on {endpoint} ...")

        return

    def start(self):
        """
            Start the Tasker Service
        """

        global DAEMON_DEBUG_MODE

        write_trace(self._pre_daemon_logfile, "Tasker daemon 'start' called ...")

        #Check to see if the pid file exists to see if the daemon is already running
        proc_id = None
        try:
            with open(self._pid_file, 'r') as pid_f:
                proc_id_str = pid_f.read().strip()
                proc_id = int(proc_id_str)

            # If we found a PID file but the process in the PID file does not exists,
            # then we are most likely reading a stale PID file.  Go ahead and startup
            # a new instance of the daemon
            if not self.process_exists(proc_id):
                os.remove(self._pid_file)
                proc_id = None

        except IOError:
            proc_id = None

        if proc_id != None:
            write_trace(self._pre_daemon_logfile, "Tasker daemon 'start' called when the service was already running.")
            sys.exit(1)

        write_trace(self._pre_daemon_logfile, "Starting the 'Tasker Service'.")

        if not DAEMON_DEBUG_MODE:
            # Start the daemon
            write_trace(self._pre_daemon_logfile, "The 'Tasker Service' is about to become a daemon.")

            try:

                self.daemonize()

                self.run()

            except SystemExit as err:
                write_trace(self._pre_daemon_logfile, "The 'Tasker Service' daemon was kicked off.")
        else:
            write_trace(self._pre_daemon_logfile, "The 'Tasker Service' skipping daemonization.")

        return


    def stop(self):
        """
            Stop the Tasker Service
        """

        write_trace(self._pre_daemon_logfile, "Tasker daemon 'stop' called ...")

        #Check to see if the PID file exists to see if the daemon is already running
        proc_id = None
        try:
            with open(self._pid_file, 'r') as pid_f:
                proc_id_str = pid_f.read().strip()
                proc_id = int(proc_id_str)
        except IOError:
            proc_id = None

        if not proc_id:
            write_trace(self._pre_daemon_logfile, "The 'Tasker Service' was not running.")
            return # This is not an error in a restart so don't exit with a error code

        # The process was running so we need to shut it down
        try:
            write_trace(self._pre_daemon_logfile, "Attempting to stop the tasker daemon ...")
            os.kill(proc_id, signal.SIGTERM)
        except OSError as os_err:
            err_str = str(os_err)
            if err_str.find("No such process") > 0:
                if os.path.exists(self._pid_file):
                    os.remove(self._pid_file)
            else:
                write_trace(self._pre_daemon_logfile, err_str)
                sys.exit(1)

        return

    def _remove_pidfile(self):
        if os.path.exists(self._pid_file):
            os.remove(self._pid_file)
        return


def tasker_daemon_main():

    global DAEMON_DEBUG_MODE

    parser = argparse.ArgumentParser("Tasker automation service.")
    parser.add_argument("action", choices=['start', 'stop', 'restart'], help="The action to perform with the service.")
    parser.add_argument("--debug", default=False, action='store_true', help="Launches the service as a non-daemon process in debug mode.")
    try:
        args = parser.parse_args()
        action = args.action
        DAEMON_DEBUG_MODE = args.debug

        if DAEMON_DEBUG_MODE:
            action = 'start'

        service = TaskerServerDaemon()
        if action == 'restart':
            service.restart()
        elif action == 'start':
            service.start()
        elif action == 'stop':
            service.stop()
        else:
            sys.stderr.write("Unknown command '%s'.\n" % action)
            sys.stderr.write("usage: %s start|stop|restart\n" % sys.argv[0])
            sys.exit(2)

    except:
        err_trace = traceback.format_exc()
        sys.stderr.write(err_trace)
        sys.exit(1)

    return


if __name__ == '__main__':

    tasker_daemon_main()

