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
import sys
from collections.abc import Sequence
from pathlib import Path
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import eyed3
import ffmpeg
import mutagen
from asserttool import ic
from asserttool import icp
from classify import classify
from click_auto_help import AHGroup
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from hashtool import hash_file
from jsontool.jsontool import jsonify_object_attributes
from libxmp.core import XMPMeta
from libxmp.utils import object_to_dict
from mptool import output
from unmp import unmp

signal(SIGPIPE, SIG_DFL)


class NotMp3FileError(ValueError):
    pass


def id3_info(
    path: Path,
    verbose: bool | int | float = False,
):
    audio_file_object = eyed3.load(path)
    # ic(audio_file_object)
    # ic(dir(audio_file_object))
    # ic(dir(audio_file_object.info))
    if not audio_file_object:
        raise NotMp3FileError
    info = audio_file_object.info
    result = jsonify_object_attributes(
        info,
        return_empty=True,
        obj_attr_list=[
            "bit_rate_str",
            "lame_tag",
            "mode",
            "sample_freq",
            "size_bytes",
            "time_secs",
        ],
    )
    # result = result | {"path": path.as_posix()}
    path_sha3_256 = hash_file(path, algorithm="sha3_256")
    # result = result | {"sha3_256": path.name}
    result = result | {"sha3_256": path_sha3_256.hex()}
    return result


def curate_id3(
    path: Path,
    return_empty: bool,
    verbose: bool | int | float = False,
):
    audio_file_object = eyed3.load(path)
    # ic(audio_file_object)
    # ic(dir(audio_file_object))
    # ic(dir(audio_file_object.info))
    if not audio_file_object:
        raise NotMp3FileError
    info = audio_file_object.info
    result = jsonify_object_attributes(
        info,
        return_empty=True,
        obj_attr_list=[
            "bit_rate_str",
            "lame_tag",
            "mode",
            "sample_freq",
            "size_bytes",
            "time_secs",
        ],
    )
    # result = result | {"path": path.as_posix()}
    path_sha3_256 = hash_file(
        path,
        algorithm="sha3_256",
    )
    # result = result | {"sha3_256": path.name}
    result = result | {"sha3_256": path_sha3_256.hex()}
    tag = audio_file_object.tag
    # ic(tag)
    # ic(dir(tag))
    # if tag:
    result_tag = jsonify_object_attributes(
        tag,
        return_empty=return_empty,
        obj_attr_list=[
            "album",
            "artist",
            "title",
        ],
        obj_attr_list_exclude=[
            "album_artist",
            "artist_origin",
            "artist_url",
            "album_type",
            "audio_file_url",
            "audio_source_url",
            "best_release_date",
            "bpm",
            "cd_id",
            "commercial_url",
            "copyright",
            "copyright_url",
            "composer",
            "disc_num",
            "encoding_date",
            "encoded_by",
            "frameiter",
            "frame_set",
            "genre",
            "getBestDate",
            "getTextFrame",
            "header",
            "images",
            "isV1",
            "isV2",
            "lyrics",
            "non_std_genre",
            "objects",
            "original_release_date",
            "parse",
            "popularities",
            "privates",
            "publisher",
            "publisher_url",
            "internet_radio_url",
            "original_artist",
            "payment_url",
            "play_count",
            "read_only",
            "recording_date",
            "release_date",
            "setTextFrame",
            "table_of_contents",
            "tagging_date",
            "terms_of_use",
            "track_num",
            "unique_file_ids",
            "user_text_frames",
            "user_url_frames",
            "version",
        ],
    )
    # ic(audio_file_object.type)
    result = result | result_tag

    if tag:
        comments = []
        for comment in tag.comments:
            if comment.description == "Audio Converter":
                continue
            if comment.text in [
                "Automated recording of The Scott Horton Show via the stream at http://scotthorton.org:8000/shs-128.m3u",
                "Cybercorder 2000 Recording    ",
            ]:
                continue
            # ic(comment.text, len(comment.text))
            # if len(comment.text) == 3:
            if comment.text == "0":
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("00000000"):
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("0036583E"):
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("0013A8F5"):
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("000DA7D1"):
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("003845B7"):
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("00384F4E"):
                # ic('skipping:', comment.text)
                continue
            if comment.text.endswith("1540170"):
                # ic('skipping:', comment.text)
                continue
            # ic(comment.description)
            # ic(comment.lang)
            comments.append(comment.text)

        chapters = []
        for chapter in tag.chapters:
            ic(chapter)
        lyrics = []
        for lyric in tag.lyrics:
            ic(lyric)
        unique_file_ids = []
        for ufid in tag.unique_file_ids:
            ic(ufid)
        # genres = []
        # for genre in tag.genre:
        #    ic(genre)

        result = result | {"comments": comments}
    else:
        result = result | {"comments": None}

    ic(result)
    return result


@click.group(no_args_is_help=True, cls=AHGroup)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )
    if not verbose:
        ic.disable()


@cli.command()
@click_add_options(click_global_options)
@click.pass_context
def metadata_mutagen(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    iterator: Sequence[dict | bytes] = unmp(valid_types=[dict, bytes])

    index = 0
    for index, _mpobject in enumerate(iterator):
        _v = Path(os.fsdecode(_mpobject)).resolve()
        ic(index, _v)
        _output_dict = {}
        _output_dict["file"] = _mpobject
        _classification = classify(
            _v,
        )
        _output_dict["classification"] = _classification
        try:
            _ = mutagen.File(_v)
        except mutagen.mp3.HeaderNotFoundError:
            continue
        else:
            for v in _.values():
                _tag_human = []
                _tag_description = v.__doc__.split()[0]
                # ic(_tag_description)
                if _tag_description == "Attached":
                    continue  # todo
                if v.HashKey.startswith("PRIV:XMP:"):
                    continue
                    _xmp = v.data.decode("utf8")
                    _xmpmeta = XMPMeta(xmp_str=_xmp)
                    # ic(_xmpmeta)  # nice xml representation
                    _xmp_dict = object_to_dict(_xmpmeta)
                    # ic(_xmp_dict)  # complicated dict
                ic(v)
                for _var in vars(v):
                    if _var == "desc":
                        _tag_human.append(getattr(v, _var).strip())

                for _var_key in vars(v):
                    _var_value = getattr(v, _var_key)  # list or str
                    if _var_key in set(["encoding", "desc", "lang"]):
                        continue  # todo

                    # ic(_tag_description, _var_key, _var_value)
                    if isinstance(_var_value, bytes):
                        continue
                    try:
                        _var_value = _var_value.strip("\x00")
                    except AttributeError:
                        _var_value = [str(_).strip("\x00") for _ in _var_value]

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
        finally:
            # print(_.pprint())
            # ic(_.tags)
            # ic(_.keys())
            output(
                _output_dict,
                reason=_mpobject,
                dict_output=dict_output,
                tty=tty,
                pretty_print=False,
            )
            if _output_dict["classification"] != "media":
                ic(_output_dict)


@cli.command()
@click_add_options(click_global_options)
@click.pass_context
def eyed3_all(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    iterator = unmp(
        valid_types=[
            bytes,
        ],
    )

    index = 0
    for index, _path in enumerate(iterator):
        path = Path(os.fsdecode(_path)).resolve()
        ic(index, path)

        audio_file_object = eyed3.load(path)
        ic(audio_file_object)
        # ic(dir(audio_file_object))
        # ic(dir(audio_file_object.info))
        result = jsonify_object_attributes(
            audio_file_object.info,
            return_empty=True,
            obj_attr_list=[
                "bit_rate",
                "bit_rate_str",
                "lame_tag",
                "mode",
                "mp3_header",
                "sample_freq",
                "size_bytes",
                "time_secs",
                "vbri_header",
                "xing_header",
            ],
        )
        ic(audio_file_object.path)
        # ic(dir(audio_file_object.tag))
        result_tag = jsonify_object_attributes(
            audio_file_object.tag,
            return_empty=True,
            obj_attr_list=[
                "album",
                "album_artist",
                "album_type",
                "artist",
                "artist_origin",
                "artist_url",
                "audio_file_url",
                "audio_source_url",
                "best_release_date",
                "bpm",
                "cd_id",
                "chapters",
                "clear",
                "comments",
                "commercial_url",
                "composer",
                "copyright",
                "copyright_url",
                "disc_num",
                "encoded_by",
                "encoding_date",
                "extended_header",
                "file_info",
                "frame_set",
                "frameiter",
                "genre",
                "getBestDate",
                "getTextFrame",
                "header",
                "images",
                "internet_radio_url",
                "isV1",
                "isV2",
                "lyrics",
                "non_std_genre",
                "objects",
                "original_artist",
                "original_release_date",
                "parse",
                "payment_url",
                "play_count",
                "popularities",
                "privates",
                "publisher",
                "publisher_url",
                "read_only",
                "recording_date",
                "release_date",
                "remove",
                "save",
                "setTextFrame",
                "table_of_contents",
                "tagging_date",
                "terms_of_use",
                "title",
                "track_num",
                "unique_file_ids",
                "user_text_frames",
                "user_url_frames",
                "version",
            ],
        )

        result_dict = result | result_tag
        # ic(audio_file_object.type)
        ic(result_dict)

        output(
            result_dict,
            reason=None,
            dict_output=dict_output,
            tty=tty,
        )


@cli.command()
@click.option("--notempty", "--not-empty", is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def eyed3_curated(
    ctx,
    notempty: bool,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    return_empty = not notempty
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    iterator = unmp(
        valid_types=[
            bytes,
        ],
    )

    index = 0
    for index, _path in enumerate(iterator):
        path = Path(os.fsdecode(_path)).resolve()
        ic(index, path)
        result = curate_id3(
            path=path,
            return_empty=return_empty,
        )
        output(
            result,
            reason=_path,
            dict_output=dict_output,
            tty=tty,
        )


@cli.command()
@click_add_options(click_global_options)
@click.pass_context
def eyed3_info(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    iterator = unmp(
        valid_types=[
            bytes,
        ],
    )

    index = 0
    for index, _path in enumerate(iterator):
        path = Path(os.fsdecode(_path)).resolve()
        ic(index, path)
        result = id3_info(
            path=path,
        )
        output(
            result,
            reason=_path,
            dict_output=dict_output,
            tty=tty,
        )


@cli.command()
@click_add_options(click_global_options)
@click.pass_context
def ffmpeg_info(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    iterator = unmp(
        valid_types=[
            bytes,
        ],
    )

    index = 0
    for index, _path in enumerate(iterator):
        path = Path(os.fsdecode(_path)).resolve()
        ic(index, path)
        _result = {}
        try:
            probe = ffmpeg.probe(path)
        except ffmpeg.Error as e:
            print(e.stderr, file=sys.stderr)
            sys.exit(1)

        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        if video_stream is None:
            print("No video stream found", file=sys.stderr)
            sys.exit(1)

        # width = int(video_stream["width"])
        # height = int(video_stream["height"])
        icp(video_stream)
        # num_frames = int(video_stream["nb_frames"])
        for _k in video_stream.keys():
            _result[_k] = video_stream[_k]
        # _result = {"width": width, "height": height, "num_frames": num_frames}
        output(
            _result,
            reason=_path,
            dict_output=dict_output,
            tty=tty,
        )
