
from typing import Callable, Optional, Tuple

import logging
import os
import stat
import time

import paramiko

from mojo.errors.exceptions import CommandError

from mojo.xmods.xformatting import indent_lines, format_command_result

from mojo.interop.protocols.ssh.sshconst import (
    DEFAULT_SSH_TIMEOUT,
    DEFAULT_SSH_RETRY_INTERVAL,
    INTERACTIVE_PROMPT,
    INTERACTIVE_PROMPT_BYTES,
    REGEX_DIRECTORY_ENTRY
)

logger = logging.getLogger()


def lookup_entry_type(pdir: str, ename: str, finfo: paramiko.SFTPAttributes) -> str:
    """
        Determines the entry type labelto assign to a file entry based on the st_mode of the file information.

        :param pdir: The parent directory of the file, passed for logging purposes.
        :param ename: The entry name of the file in the directory listing.
        :param finfo: The file information as returned by lstat on the file entry.

        :returns: A label indicating the type of directory entry.
    """
    etype = None
    if stat.S_ISREG(finfo.st_mode):
        etype = "file"
    elif stat.S_ISDIR(finfo.st_mode):
        etype = "dir"
    elif stat.S_ISLNK(finfo.st_mode):
        etype = "link"
    elif stat.S_ISCHR(finfo.st_mode):
        etype = "char"
    elif stat.S_ISBLK(finfo.st_mode):
        etype = "block"
    else:
        print ("ERROR: Unknown entry type. pdir=%s, ename=%s" % (pdir, ename))

    return etype

def primitive_list_directory(ssh_client: paramiko.SSHClient, directory: str) -> dict:
    """
        Uses a primitive method to create a list of the files and folders in a directory
        by running the 'ls -al' commands on the directory.  This is required if the SSH
        server does not support sftp.

        :param ssh_client: A :class:`paramiko.SSHClient` object that has already been connected
                           to the remote server.
        :param directory: The remote directory to get a list catalog for.

        :returns: A dictionary with the information about the items in the target directory.
    """
    entries = None

    ls_cmd = "ls -al %s" % directory

    status, stdout, stderr = ssh_execute_command(ssh_client, ls_cmd)

    if status == 0:
        entries = primitive_parse_directory_listing(directory, stdout)
    else:
        # Allow permission denied errors
        if stderr.find("Permission denied") < 0:
            errmsg = "Error attempting to get a primitive directory listing.\n    CMD=%s\n    STDERR:\n%s" % (ls_cmd, stderr)
            raise Exception(errmsg)

    return entries

def primitive_list_tree(ssh_client: paramiko.SSHClient, treeroot: str, max_depth: int=1) -> dict:
    """
        Uses a primitive method to create an information tree about the files and folders
        in a directory tree by running 'ls -al' commands on the directory tree.  This is
        required if the SSH server does not support sftp.

        :param ssh_client: A :class:`paramiko.SSHClient` object that has already been connected
                           to the remote server.
        :param treeroot: The remote root directory to get a directory tree catalog for.
        :param max_depth: The maximum descent depth to go to when building the tree catalog.

        :returns: A dictionary with the information about the root directory and its children.
    """

    level_items = primitive_list_directory(ssh_client, treeroot)

    if max_depth > 1:
        if not treeroot.endswith("/"):
            treeroot = treeroot + "/"

        for nxtitem in level_items.values():
            nxtname = nxtitem["name"]
            if nxtitem["type"] == "dir":
                nxtroot = treeroot + nxtname
                nxtchildren = primitive_list_tree_recurse(ssh_client, nxtroot, max_depth - 1)
                nxtitem.update(nxtchildren)

    tree_info = {
        "name": treeroot,
        "items": level_items
    }

    return tree_info

def primitive_list_tree_recurse(ssh_client: paramiko.SSHClient, targetdir: str, remaining: int) -> dict:
    """
        Method which is called recursively to list the items in a directory and to form a tree
        of information about the files under a room directory.  This method utilizes primitive
        shell commands in order to get directory information and is used when the SSH server on a
        device does not support FTP based access or file queries

        :params ssh_client: A paramiko.SSHClient to use for running commands to discover the information
                            about a directory.
        :params targetdir: The target directory of the local tree to scan.
        :params remaining: The remaining levels to descend

        :returns: A dictionary with the information about the target directory and its children.
    """

    level_items = primitive_list_directory(ssh_client, targetdir)

    if remaining > 1:
        if not targetdir.endswith("/"):
            targetdir = targetdir + "/"

        for nxtitem in level_items.values():
            nxtname = nxtitem["name"]
            if nxtitem["type"] == "dir":
                nxttarget = targetdir + nxtname
                nxtchildren = primitive_list_tree_recurse(ssh_client, nxttarget, remaining - 1)
                nxtitem.update(nxtchildren)

    children_info = {
        "items": level_items
    }

    return children_info

def primitive_parse_directory_listing(listing_dir:str, content: str) -> dict:
    """
        Method which is called parse the information associated with a directory listing.

        :params listing_dir: The directory path associated with the directory listing content being parsed.
        :params content: The directory listing content to be parsed.

        :returns: A dictionary with the directory entry items from a directoy based on the directory listing content being parsed.
    """
    entries = {}

    listing_lines = content.splitlines(False)
    for nxtline in listing_lines:
        nxtline = nxtline.strip()

        mobj = REGEX_DIRECTORY_ENTRY.match(nxtline)
        if mobj is not None:
            mgroups = mobj.groups()

            name = mgroups[6]
            if name == "." or name == "..":
                continue

            perms = mgroups[0]

            perms_tc = perms[0]
            etype = None
            if perms_tc == '-':
                etype = "file"
            elif perms_tc == 'd':
                etype = "dir"
            elif perms_tc == 'l':
                etype = "link"
                name, _ = name.split(" -> ")
            elif perms_tc == 'c':
                etype = "char"
            elif perms_tc == 'b':
                etype = "block"
            else:
                raise Exception("Unknown directory listing entry type. dir=%s tc=%s" % (listing_dir, perms_tc))

            dentry = {
                "name": name,
                "perms": perms,
                "type": etype,
                "owner": mgroups[2],
                "group": mgroups[3],
                "size": mgroups[4],
                "modified": mgroups[5]
            }

            entries[name] = dentry

    return entries

def primitive_directory_exists(ssh_client: paramiko.SSHClient, remotedir: str) -> bool:
    """
        Checks to see if the specified file exists.

        :param ssh_client: A paramiko.SSHClient to run commands over.
        :param remotedir: The path of the remote directory to check for existance.

        :returns: A boolean indicating if the file exists.
    """
    exists = False

    existscmd = 'test -d {0} && echo exists'.format(remotedir)
    status, stdout, stderr = ssh_execute_command(ssh_client, existscmd)

    if status == 0:
        exists = stdout.strip() == 'exists'

    return exists

def primitive_file_exists(ssh_client: paramiko.SSHClient, remotepath: str) -> bool:
    """
        Checks to see if the specified file exists.

        :param ssh_client: A paramiko.SSHClient to run commands over.
        :param remotepath: The path of the remote file to check for existance.

        :returns: A boolean indicating if the file exists.
    """
    exists = False

    existscmd = 'test -f {0} && echo exists'.format(remotepath)
    status, stdout, stderr = ssh_execute_command(ssh_client, existscmd)

    if status == 0:
        exists = stdout.strip() == 'exists'

    return exists

def primitive_file_pull(ssh_client: paramiko.SSHClient, remotepath: str, localpath: str):
    """
        Pulls the contents of a file to a local path using a primitive 'cat' command.

        :param ssh_client: A paramiko.SSHClient to run commands over.
        :param remotepath: The path to the file on the remote machine.
        :param localpath: The local path to a file to write the contents of the remote file too.
    """
    copycmd = "cat %s" % remotepath

    status, stdout, stderr = ssh_execute_command(ssh_client, copycmd, decode=False)

    if status != 0:
        stderr = stderr.decode()
        errmsg_lines = [
            "Error pulling file using command. cmd=%s" % copycmd,
            "STDERR:",
            indent_lines(stderr, 1)
        ]
        raise Exception(os.linesep.join(errmsg_lines))

    with open(localpath, 'wb') as lfile:
        lfile.write(stdout)

    return

def primitive_file_push(ssh_client: paramiko.SSHClient, localpath: str, remotepath: str, read_size: int=1024):
    """
        Pushes the contents of a local file to a file on a remote machine at the path specified by remotepath.

        :param ssh_client: A paramiko.SSHClient to run commands over.
        :param localpath: The local path to a file to read contents from.
        :param remotepath: The path to file on the remote machine to write the contents of the local file too.
    """
    cat_cmd = "cat > {}".format(remotepath)

    with open(localpath, "rb") as file:
        content = file.read()
        status, stdout, stderr = ssh_execute_command(ssh_client, command=cat_cmd, chunk_size=read_size, input=content, decode=False)
        if status != 0:
            errmsg = "Error pushing file={} to remote path.".format(remotepath)
            fmt_errmsg = format_command_result(errmsg, cat_cmd, status, stdout.decode(), stderr.decode())
            raise CommandError(fmt_errmsg)

    return

def sftp_list_directory(sftp, directory, userlookup, grouplookup) -> dict:
    """
        Gets a listing of the directory entries of a remote directory.

        :param sftp: A paramiko.SFTPClient that is connected to a remote machine.
        :param directory: The remote directory to get the directory listing for.
        :param userlookup: A dictionary to utilize in order to lookup the user associated with a directory item.
        :param grouplookup: A dictionary to utilize in order to lookup the group associated with a directory item.

        :returns: A dictionary with the information about the items in the target directory.
    """
    entries = {}

    try:
        sftp.chdir(directory)
        directory_items = sftp.listdir()

        for nname in directory_items:

            try:
                ninfo = sftp.lstat(nname)
                perms = ""
                dentry = {
                    "name": nname,
                    "perms": perms,
                    "type": lookup_entry_type(directory, nname, ninfo),
                    "owner": userlookup(ninfo.st_uid),
                    "group": grouplookup(ninfo.st_gid),
                    "size": ninfo.st_size,
                    "accessed": ninfo.st_atime,
                    "modified": ninfo.st_mtime
                }

                entries[nname] = dentry
            except PermissionError:
                logger.exception("Unable to perform lstat on remote directory item %r." % nname)
    except PermissionError:
        logger.exception("Unable to perform listdir on remote directory %r." % directory)

    return entries

def sftp_list_tree(sftp: paramiko.SFTPClient, treeroot: str, userlookup: Callable[[int, Optional[bool]], str], grouplookup: Callable[[int, Optional[bool]], str], max_depth: int=1) -> dict:
    """
        Gets a tree of the directory entries of a remote directory.

        :param sftp: A paramiko.SFTPClient that is connected to a remote machine.
        :param treeroot: The root directory to get the directory listing for.
        :param userlookup: A dictionary to utilize in order to lookup the user associated with a directory item.
        :param grouplookup: A dictionary to utilize in order to lookup the group associated with a directory item.
        :param max_depth: The depth to which to create a directory tree.

        :returns: A dictionary with the information about the root directory and its children.
    """
    level_items = sftp_list_directory(sftp, treeroot, userlookup, grouplookup)

    if max_depth > 1:
        if not treeroot.endswith("/"):
            treeroot = treeroot + "/"

        for nxtitem in level_items.values():
            nxtname = nxtitem["name"]
            if nxtitem["type"] == "dir":
                nxtroot = treeroot + nxtname
                nxtchildren = sftp_list_tree_recurse(sftp, nxtroot, userlookup, grouplookup, max_depth - 1)
                nxtitem.update(nxtchildren)

    tree_info = {
        "name": treeroot,
        "items": level_items
    }

    return tree_info

def sftp_list_tree_recurse(sftp: paramiko.SFTPClient, targetdir: str, userlookup: Callable[[int, Optional[bool]], str], grouplookup: Callable[[int, Optional[bool]], str], remaining: int) -> dict:
    """
        Gets a listing of the directory passed and then recursively calls itself to create sub directory listings up to the remaining depth.

        :param sftp: A paramiko.SFTPClient that is connected to a remote machine.
        :param targetdir: The target directory to get the directory tree listing for.
        :param userlookup: A dictionary to utilize in order to lookup the user associated with a directory item.
        :param grouplookup: A dictionary to utilize in order to lookup the group associated with a directory item.
        :param max_depth: The depth to which to create a directory tree.

        :returns: A dictionary with the information about the target directory and its children.
    """
    level_items = sftp_list_directory(sftp, targetdir, userlookup, grouplookup)

    if remaining > 1:
        if not targetdir.endswith("/"):
            targetdir = targetdir + "/"

        for nxtitem in level_items.values():
            nxtname = nxtitem["name"]
            if nxtitem["type"] == "dir":
                nxtroot = targetdir + nxtname
                nxtchildren = sftp_list_tree_recurse(sftp, nxtroot, userlookup, grouplookup, remaining - 1)
                nxtitem.update(nxtchildren)

    children_info = {
        "items": level_items
    }

    return children_info

def ssh_execute_command(ssh_client: paramiko.SSHClient, command: str, pty_params=None,
                        inactivity_timeout: float=DEFAULT_SSH_TIMEOUT, inactivity_interval: float=DEFAULT_SSH_RETRY_INTERVAL,
                        chunk_size: int=1024, input: Optional[str]=None, decode=True) -> Tuple[int, str, str]:
    """
        Runs a command on a remote server using the specified ssh_client.  We implement our own version of ssh_execute_command
        in order to have better control over the timeouts and to make sure all the checks are sequenced properly in order
        to prevent SSH lockups.

        :param ssh_client: The :class:`paramiko.SSHClient` object to utilize when running the command.
        :param command: The commandline to run.
        :param inactivity_timeout: The timeout for the channel for the ssh transaction.
        :param inactivity_interval: The retry interval to wait for the channel to have data ready.
        :param chunk_size: The size of the chunks that are read during receive operations

        :returns: A tuple with the command result code, the standard output and the standard error output.
    """
    status = None
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()

    start_time = time.time()
    end_time = start_time + inactivity_timeout

    channel = ssh_client.get_transport().open_session(timeout=inactivity_timeout)

    if pty_params is not None:
        channel.get_pty(**pty_params)

    channel.exec_command(command)

    input_length = 0
    if input is not None:
        if isinstance(input, str):
            input = input.encode()
        input_length = len(input)
    input_pos = 0
    input_shutdown = False

    while True:
        # Grab exit status ready before checking to see if stdout_ready or stderr_ready are True
        exit_status_ready = channel.exit_status_ready()
        stdout_ready = channel.recv_ready()
        stderr_ready = channel.recv_stderr_ready()

        # If stdout_ready or stderr_ready are true, we read this round
        if stdout_ready or stderr_ready:
            if stdout_ready:
                rcv_data = channel.recv(chunk_size)
                stdout_buffer.extend(rcv_data)
            if stderr_ready:
                rcv_data = channel.recv_stderr(chunk_size)
                stderr_buffer.extend(rcv_data)

            # We only want to timeout if there is inactivity
            start_time = time.time()
            end_time = start_time + inactivity_timeout

        # If there is data left to send and the send channel is ready
        # for input, send a chunk from the input buffer 
        elif input_length > 0 and input_pos < input_length and channel.send_ready():

            send_size = chunk_size
            avail_length = input_length - input_pos
            if avail_length < chunk_size:
                send_size = avail_length

            send_chunk = input[input_pos: input_pos + send_size]
            sent_size = channel.send(send_chunk)

            input_pos = input_pos + sent_size

        # If we have written everything there is to write, and writting to the
        # channel has not been shutdown, then shutdown writing.
        elif input is not None and not input_shutdown and input_pos >= input_length:
            channel.shutdown_write()
            input_shutdown = True

        # If we did not read any data this round and our exit status was ready, its time to exit
        elif exit_status_ready:
            status = channel.recv_exit_status()
            break
        # We didn't have any data to read and our exit status was not ready, go to sleep for interval
        else:
            now_time = time.time()
            if now_time > end_time:
                diff_time = now_time - start_time
                peername = ssh_client.get_transport().sock.getpeername()
                err_msg = "Timeout while executing SSH command.\n  peer=%r  command=%s\n  start=%r end=%r now=%r diff=%r" % (
                    peername, command, start_time, end_time, now_time, diff_time)
                raise TimeoutError(err_msg)

            # If we did not timeout, go to sleep for the interval before we make another attempt to read
            time.sleep(inactivity_interval)

        # End while True

    stdout = stdout_buffer
    if decode:
        stdout = stdout_buffer.decode()
    del stdout_buffer

    stderr = stderr_buffer
    if decode:
        stderr = stderr_buffer.decode()
    del stderr_buffer

    return status, stdout, stderr

def ssh_execute_command_in_channel(ssh_channel: paramiko.Channel, command: str, read_timeout: float=2, inactivity_timeout: float=DEFAULT_SSH_TIMEOUT, inactivity_interval: float=DEFAULT_SSH_RETRY_INTERVAL, chunk_size: int=1024, status_check=False) -> Tuple[int, str, str]:
    """
        Runs a command on a remote server using the specified ssh_client.  We implement our own version of ssh_execute_command
        in order to have better control over the timeouts and to make sure all the checks are sequenced properly in order
        to prevent SSH lockups.

        :param ssh_client: The :class:`paramiko.SSHClient` object to utilize when running the command.
        :param command: The commandline to run.
        :param inactivity_timeout: The timeout for the channel for the ssh transaction.
        :param inactivity_interval: The retry interval to wait for the channel to have data ready.
        :param chunk_size: The size of the chunks that are read during receive operations

        :returns: A tuple with the command result code, the standard output and the standard error output.
    """
    status = None
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()

    start_time = time.time()
    end_time = start_time + inactivity_timeout

    ssh_channel.sendall(command + "\n")

    stdout_pipe_timeout = 0
    stderr_pipe_timeout = 0
    while True:
        if stdout_pipe_timeout < 2:
            try:
                rcv_data = ssh_channel.in_buffer.read(chunk_size, read_timeout)
                stdout_buffer.extend(rcv_data)
                if rcv_data.endswith(INTERACTIVE_PROMPT_BYTES):
                    stdout_pipe_timeout = 2
            except paramiko.buffered_pipe.PipeTimeout:
                stdout_pipe_timeout += 1

        if stderr_pipe_timeout < 2:
            try:
                rcv_data = ssh_channel.in_stderr_buffer.read(chunk_size, read_timeout)
                stderr_buffer.extend(rcv_data)
            except paramiko.buffered_pipe.PipeTimeout:
                stderr_pipe_timeout += 1

        if stdout_pipe_timeout > 1 and stderr_pipe_timeout > 1:
            break

        now_time = time.time()
        if now_time > end_time:
            errmsg = "Timeout while running command={}".format(command)
            raise TimeoutError(errmsg)
        # End while True

    if not status_check:
        _, status_stdout, _ = ssh_execute_command_in_channel(ssh_channel, "echo $?", read_timeout=read_timeout, inactivity_timeout=inactivity_timeout, inactivity_interval=inactivity_interval, chunk_size=chunk_size, status_check=True)
        status = int(status_stdout)

    stdout = stdout_buffer.decode()
    del stdout_buffer

    if not stdout.startswith(command):
        errmsg = "The first line should have been an echo of our command."
        raise Exception(errmsg)

    if not stdout.endswith(INTERACTIVE_PROMPT):
        errmsg = "The first line should have been an echo of our command."
        raise Exception(errmsg)

    stdout = stdout[len(command):-len(INTERACTIVE_PROMPT)].strip()

    stderr = stderr_buffer.decode()
    del stderr_buffer

    return status, stdout, stderr
