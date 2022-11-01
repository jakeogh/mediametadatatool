#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tab-width:4

# pylint: disable=useless-suppression             # [I0021]
# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=missing-param-doc               # [W9015]
# pylint: disable=missing-module-docstring        # [C0114]
# pylint: disable=fixme                           # [W0511] todo encouraged
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

import os
from collections.abc import Sequence
from pathlib import Path
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import mutagen
import sh
from asserttool import ic
from click_auto_help import AHGroup
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from eprint import eprint
from libxmp.core import XMPMeta
from libxmp.utils import object_to_dict
from mptool import mpd_enumerate
from mptool import output
from timetool import get_timestamp
from unmp import unmp

# from prettytable import PrettyTable
# output_table = PrettyTable()


sh.mv = None  # use sh.busybox('mv'), coreutils ignores stdin read errors


# this should be earlier in the imports, but isort stops working
signal(SIGPIPE, SIG_DFL)


@click.group(no_args_is_help=True, cls=AHGroup)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
) -> None:

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )


@cli.command()
@click_add_options(click_global_options)
@click.pass_context
def metadata(
    ctx,
    verbose: bool | int | float,
    verbose_inf: bool,
    dict_output: bool,
) -> None:

    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    iterator: Sequence[dict | bytes] = unmp(valid_types=[dict, bytes], verbose=verbose)

    index = 0
    _k = None
    for index, _mpobject in enumerate(iterator):
        _v = Path(os.fsdecode(_mpobject)).resolve()
        _ = mutagen.File(_v)
        if verbose:
            ic(index, _v)

        ic(type(_), dir(_))
        # for frame in _.tags.getall():
        #    ic(frame)
        for v in _.values():
            ic(dir(v))
            ic(v.FrameID)
            ic(v.HashKey)
            if v.HashKey.startswith("PRIV:XMP:"):
                _xmp = v.data
                ic(_xmp)
                xmpmeta = XMPMeta(xmp_str=_xmp)
                ic(xmpmeta)
                # _xmp_dict = object_to_dict(_xmp)
            ic(v)
        # print(_.pprint())
        # ic(_.tags)
        # ic(_.keys())
        # output(
        #    _,
        #    reason=_mpobject,
        #    dict_output=dict_output,
        #    tty=tty,
        #    verbose=verbose,
        #    pretty_print=True,
        # )
