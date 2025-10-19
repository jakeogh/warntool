#!/usr/bin/env python3
# -*- coding: utf8 -*-


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
    symlink_ok: bool,
    msg: None | str = None,
    disk_size: None | str = None,
):
    assert isinstance(devices, tuple)
    disk_gib_set = set()
    for device in devices:
        device = Path(device)
        assert path_is_block_special(device, symlink_ok=symlink_ok)
        assert not block_special_path_is_mounted(
            device.resolve(),
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
        if not disk_size:
            answer = input(
                "Do you want to delete all of your data? (type the size of the disk to proceed): "
            )
        else:
            answer = disk_size
        if answer != disk_gib:
            ic(f"INCORRECT, the size in GiB is: {disk_gib}, not {answer}:")
            sys.exit(1)

    eprint("Sleeping 5 seconds, press CTRL-c to cancel")
    time.sleep(5)
