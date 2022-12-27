#!/usr/bin/env python3
# -*- coding: utf8 -*-


# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=C0114  #      Missing module docstring (missing-module-docstring)
# pylint: disable=fixme                           # [W0511] todo is encouraged
# pylint: disable=line-too-long                   # [C0301]
# pylint: disable=too-many-instance-attributes    # [R0902]
# pylint: disable=too-many-lines                  # [C0302] too many lines in module
# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement

from __future__ import annotations

import sys
import time
from pathlib import Path
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

from asserttool import ic
from eprint import eprint
from mounttool import block_special_path_is_mounted
from pathtool import path_is_block_special
from run_command import run_command

signal(SIGPIPE, SIG_DFL)


def warn(
    devices,
    *,
    msg: None | str = None,
    verbose: bool | int | float = False,
):

    assert isinstance(devices, tuple)
    disk_gib_set = set()
    for device in devices:
        device = Path(device)
        assert path_is_block_special(device)
        assert not block_special_path_is_mounted(
            device,
            verbose=verbose,
        )

        if msg:
            eprint(msg)
        else:
            devices_as_posix = [Path(device).as_posix() for device in devices]
            eprint(
                "THIS WILL DESTROY ALL DATA ON",
                " ".join(devices_as_posix),
                "_REMOVE_ ANY HARD DRIVES (and removable storage like USB sticks) WHICH YOU DO NOT WANT TO ACCIDENTLY DELETE THE DATA ON",
            )
            del devices_as_posix

        fdisk_command = ["fdisk", "--list", device.as_posix()]
        output = run_command(
            fdisk_command,
            expected_exit_status=0,
            str_output=True,
            verbose=verbose,
        )
        print(output, file=sys.stderr)
        disk_gib = output.split(f"Disk {device}: ")
        disk_gib = disk_gib[1].split(" ")[0]
        # ic(disk_gib)
        float(disk_gib)
        disk_gib_set.add(disk_gib)
        if len(list(disk_gib_set)) > 1:
            ic(disk_gib_set)
            raise ValueError("disks are not the same size!", list(disk_gib_set))
        print("")
        answer = input(
            "Do you want to delete all of your data? (type the size of the disk to proceed): "
        )
        if answer != disk_gib:
            ic("INCORRECT, the size in GiB is: {}, not {}:".format(disk_gib, answer))
            sys.exit(1)

    eprint("Sleeping 5 seconds")
    time.sleep(5)
