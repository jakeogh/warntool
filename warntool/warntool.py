#!/usr/bin/env python3
# -*- coding: utf8 -*-

# flake8: noqa           # flake8 has no per file settings :(
# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=C0114  #      Missing module docstring (missing-module-docstring)
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement
# pylint: disable=C0305  # Trailing newlines editor should fix automatically, pointless warning
# pylint: disable=C0413  # TEMP isort issue [wrong-import-position] Import "from pathlib import Path" should be placed at the top of the module [C0413]

import os
import sys
import time
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import sh

signal(SIGPIPE, SIG_DFL)
from pathlib import Path
from typing import ByteString
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

#from with_sshfs import sshfs
#from with_chdir import chdir
from asserttool import eprint
from asserttool import ic
from asserttool import nevd
#from asserttool import validate_slice
#from asserttool import verify
#from enumerate_input import enumerate_input
from mounttool import block_special_path_is_mounted
from pathtool import path_is_block_special
#from retry_on_exception import retry_on_exception
from run_command import run_command


def warn(devices, *, msg=None):
    assert isinstance(devices, tuple)
    disk_gib_set = set()
    for device in devices:
        device = Path(device)
        assert path_is_block_special(device)
        assert not block_special_path_is_mounted(device, verbose=False, debug=False)

        if msg:
            eprint(msg)
        else:
            devices_as_posix = [device.as_posix() for device in devices]
            eprint("THIS WILL DESTROY ALL DATA ON", ' '.join(devices_as_posix), "_REMOVE_ ANY HARD DRIVES (and removable storage like USB sticks) WHICH YOU DO NOT WANT TO ACCIDENTLY DELETE THE DATA ON")
            del devices_as_posix

        fdisk_command = ["fdisk", "--list", device.as_posix()]
        output = run_command(fdisk_command, expected_exit_status=0, str_output=True)
        print(output, file=sys.stderr)
        disk_gib = output.split('Disk {}: '.format(device))
        #ic(disk_gib)
        disk_gib = disk_gib[1].split(' ')[0]
        #ic(disk_gib)
        float(disk_gib)
        disk_gib_set.add(disk_gib)
        if len(list(disk_gib_set)) > 1:
            ic(disk_gib_set)
            raise ValueError('disks are not the same size!', list(disk_gib_set))
        print("")
        answer = input("Do you want to delete all of your data? (type the size of the disk in GiB to proceed): ")
        if answer != disk_gib:
            ic('INCORRECT, the size in GiB is: {}, not {}:'.format(disk_gib, answer))
            sys.exit(1)

    eprint("Sleeping 5 seconds")
    time.sleep(5)


@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def cli(ctx,
        verbose: bool,
        debug: bool,
        ):

    null, end, verbose, debug = nevd(ctx=ctx,
                                     printn=False,
                                     ipython=False,
                                     verbose=verbose,
                                     debug=debug,)

