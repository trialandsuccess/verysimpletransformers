import io
import zlib
from pathlib import Path

import pytest
import torch.cuda
from configuraptor import asbytes
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import pandas as pd
import logging
import dill

from src.verysimpletransformers.core import from_vst, to_vst, write_bundle, run_metadata_checks
from src.verysimpletransformers.metadata import get_metadata, compare_versions
from src.verysimpletransformers.versioning import get_version
from src.verysimpletransformers.metadata_schema import MetaHeader, Metadata, Version
from src.verysimpletransformers.types import DummyModel

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)


def test_metadata():
    valid_meta = get_metadata(0, 0, "cpu").meta_header

    assert "MetaHeader<" in repr(valid_meta)

    valid_meta = asbytes(valid_meta)
    meta_len = len(valid_meta)
    valid_meta = io.BytesIO(valid_meta)
    assert run_metadata_checks(valid_meta, meta_len) is None

    with pytest.warns(BytesWarning):
        # invalid length-meta combi leads to Byteswarning
        run_metadata_checks(valid_meta, 20)


def test_version():
    v = Version()

    v.major = 1
    v.minor = 2
    v.patch = 3

    v2 = Version()

    v2.major = 1
    v2.minor = 3
    v2.patch = 3

    v3 = Version()

    v3.major = 2
    v3.minor = 3
    v3.patch = 3

    v4 = Version()

    v4.major = 1
    v4.minor = 2
    v4.patch = 31

    assert repr(v) == "Version<1.2.3>"

    compare_versions('same', v, None)  # missing one
    compare_versions('same', v, v)  # same, no issue
    compare_versions("patch", v, v4)  # patch change

    with pytest.warns(UserWarning):
        compare_versions('minor', v, v3)  # major change

    with pytest.warns(UserWarning):
        compare_versions('minor', v, v2)  # minor change


def test_bundle():
    # Optional model configuration
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
        model = ClassificationModel(
            "bert", "prajjwal1/bert-small", args=model_args,
            use_cuda=torch.cuda.is_available()
        )

        # Train the model
        model.train_model(train_df)

    fp = Path("pytest1.vst")
    to_vst(model, fp, compression=0)

    new_model = from_vst(fp)

    # assert hasattr(model, 'predict')
    # assert not hasattr(model, 'predictx')
    assert hasattr(new_model, 'predict')
    assert not hasattr(new_model, 'predictx')


def test_backwards_compat():
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

    fp = Path('pytest0.vst')
    with fp.open("wb") as output_file:
        write_bundle(output_file, hashbang, meta._pack(), pickled)

    new_model = from_vst(fp)
    assert hasattr(new_model, 'predict')
    assert not hasattr(new_model, 'predictx')

    assert new_model.predict("something") == "gnihtemos" == model.predict("something") == model.predict(["something"])[
        0]
