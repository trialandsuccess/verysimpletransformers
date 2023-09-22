import io
import logging
import typing
import zlib
from pathlib import Path

import dill
import pandas as pd
import pytest
import torch.cuda
from configuraptor import asbytes
from simpletransformers.classification import ClassificationArgs, ClassificationModel

from src.verysimpletransformers.core import (
    _from_vst,
    from_vst,
    from_vst_with_metadata,
    run_metadata_checks,
    simple_load,
    to_vst,
    upgrade_metadata,
    write_bundle,
)
from src.verysimpletransformers.exceptions import CorruptedModelException, custom_excepthook
from src.verysimpletransformers.metadata import compare_versions, get_metadata
from src.verysimpletransformers.metadata_schema import Metadata, MetaHeader, Version
from src.verysimpletransformers.support import as_binaryio
from src.verysimpletransformers.types import DummyModel, SimpleTransformerProtocol
from src.verysimpletransformers.versioning import get_version


def _get_v0_dummy(fp: Path):
    v0_metadata = get_version(MetaHeader, 0)()
    v0_metadata.welcome_text = "Welcome to VST!"

    model = DummyModel()
    pickled = dill.dumps(model)
    pickled = zlib.compress(pickled, level=0)  # compression of 0 still slightly changes the bytes!

    hashbang = b"#!/usr/bin/env verysimpletransformers\n"
    meta = Metadata()

    meta.meta_version = 0  # <-
    meta.meta_length = v0_metadata._get_length()
    meta.content_length = len(pickled)
    meta.meta_header = v0_metadata

    with fp.open("wb") as output_file:
        write_bundle(output_file, hashbang, meta._pack(), pickled)

    return model

def _get_v1_dummy(fp: Path):
    FAST = True

    if FAST:
        model = DummyModel()
    else:
        # Preparing train data
        train_data = [
            ["Aragorn was the heir of Isildur", 1],
            ["Frodo was the heir of Isildur", 0],
        ]
        train_df = pd.DataFrame(train_data)
        train_df.columns = ["text", "labels"]

        # Preparing eval data
        eval_data = [
            ["Theoden was the king of Rohan", 1],
            ["Merry was the king of Rohan", 0],
        ]
        eval_df = pd.DataFrame(eval_data)
        eval_df.columns = ["text", "labels"]

        model_args = ClassificationArgs(
            num_train_epochs=1,
            overwrite_output_dir=True,
            save_model_every_epoch=False,
        )

        # Create a ClassificationModel
        model = ClassificationModel("bert", "prajjwal1/bert-small", args=model_args, use_cuda=torch.cuda.is_available())

        # Train the model
        model.train_model(train_df)

    to_vst(model, fp, compression="zero") # illegal but should automatically be changed to 0 (int)

    return model

def _get_corrupted_vst(reason: typing.Literal["pickling", "compression"]):
    pickled = b"wrong"

    if reason == "pickling":
        pickled = zlib.compress(pickled, level=1)  # compression of 0 still slightly changes the bytes!

    file = io.BytesIO()
    output_file = as_binaryio(file, "wb")

    hashbang = b"#!/usr/bin/env verysimpletransformers\n"
    metadata = asbytes(get_metadata(len(pickled), compression_level=0, device="cpu"))

    write_bundle(output_file, hashbang, metadata, pickled)

    return as_binaryio(file, "rb")
