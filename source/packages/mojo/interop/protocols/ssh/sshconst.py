"""
.. module:: sshconst
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing ssh constants

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


import dataclasses
import os
import re

from mojo.credentials.sshcredential import SshCredential

DEFAULT_SSH_TIMEOUT = 300
DEFAULT_SSH_RETRY_INTERVAL = .5

DEFAULT_FAILURE_LABEL = "Failure"
DEFAULT_SUCCESS_LABEL = "Success"

INTERACTIVE_PROMPT="PROMPT%:%:%"
INTERACTIVE_PROMPT_BYTES = INTERACTIVE_PROMPT.encode('utf-8')

TEMPLATE_COMMAND_FAILURE = "RUNCMD%s: {} running CMD=%s{}STDOUT:{}%s{}STDERR:{}%s".format(DEFAULT_FAILURE_LABEL, *([os.linesep] * 4))
TEMPLATE_COMMAND_SUCCESS = "RUNCMD%s: {} running CMD=%s{}STDOUT:{}%s{}STDERR:{}%s".format(DEFAULT_SUCCESS_LABEL, *([os.linesep] * 4))

#                    PERMS          LINKS   OWNER       GROUPS    SIZE   MONTH  DAY  TIME    NAME
#                  rwxrwxrwx         24      myron      myron     4096   Jul    4   00:37  PCBs
REGEX_DIRECTORY_ENTRY = re.compile(r"([\S]+)[\s]+([0-9]+)[\s]+([\S]+)[\s]+([\S]+)[\s]+([0-9]+)[\s]+([A-za-z]+[\s]+[0-9]+[\s]+[0-9:]+)[\s]+([\S\s]+)")


@dataclasses.dataclass
class SshJumpParams:
    host: str
    credential: SshCredential
    port: int = 22
