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
    for index, _mpobject in enumerate(iterator):
        _v = Path(os.fsdecode(_mpobject)).resolve()
        _ = mutagen.File(_v)
        ic(index, _v)
        _output_dict = {}
        _output_dict["file"] = _mpobject
        for v in _.values():
            _tag_human = []
            _tag_description = v.__doc__.split()[0]
            ic(_tag_description)
            if v.HashKey.startswith("PRIV:XMP:"):
                continue
                _xmp = v.data.decode("utf8")
                _xmpmeta = XMPMeta(xmp_str=_xmp)
                # ic(_xmpmeta)  # nice xml representation
                _xmp_dict = object_to_dict(_xmpmeta)
                # ic(_xmp_dict)  # complicated dict
            if verbose:
                ic(v)
            for _var in vars(v):
                if _var == "desc":
                    _tag_human.append(getattr(v, _var).strip())

            for _var_key in vars(v):
                _var_value = getattr(v, _var_key)  # list or str
                if _var_key in set(["encoding", "desc", "lang"]):
                    continue  # todo

                # ic(_var_key, _var_value)
                try:
                    _var_value = _var_value.strip("\x00")
                except AttributeError:
                    _var_value = [_.strip("\x00") for _ in _var_value]

                # ic(_var_key, _var_value)
                if isinstance(_var_value, list):
                    _var_value = [_.strip() for _ in _var_value]
                else:
                    _var_value = _var_value.strip()

                if isinstance(_var_value, list):
                    _var_value = " ".join(_var_value)

                # ic(_var_key, _var_value)
                _tag_human.append(_var_value)
                _output_dict[_tag_description] = " ".join(_tag_human)

        # print(_.pprint())
        # ic(_.tags)
        # ic(_.keys())
        output(
            _output_dict,
            reason=_mpobject,
            dict_output=dict_output,
            tty=tty,
            verbose=verbose,
            pretty_print=False,
        )
