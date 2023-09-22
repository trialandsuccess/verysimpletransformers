import io
import logging
import zlib
from pathlib import Path

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
from src.verysimpletransformers.metadata_schema import Metadata, Version
from src.verysimpletransformers.support import as_binaryio
from src.verysimpletransformers.types import DummyModel, SimpleTransformerProtocol
from tests.helpers_for_test import _get_v0_dummy, _get_corrupted_vst, _get_v1_dummy

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)


def test_metadata():
    valid_meta = get_metadata(0, 0, "cpu").meta_header

    assert "MetaHeader<" in repr(valid_meta)

    valid_meta = asbytes(valid_meta)
    meta_len = len(valid_meta)
    valid_meta = io.BytesIO(valid_meta)
    assert run_metadata_checks(valid_meta, meta_len)[0]

    with pytest.warns(UserWarning):
        assert not run_metadata_checks(valid_meta, meta_len, version=999)[0]

    with pytest.warns(BytesWarning):
        # invalid length-meta combi leads to Byteswarning
        assert not run_metadata_checks(valid_meta, 20)[0]


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

    compare_versions("same", v, None)  # missing one
    compare_versions("same", v, v)  # same, no issue
    compare_versions("patch", v, v4)  # patch change

    with pytest.warns(UserWarning):
        compare_versions("minor", v, v3)  # major change

    with pytest.warns(UserWarning):
        compare_versions("minor", v, v2)  # minor change


def test_bundle():
    # Optional model configuration

    fp = Path("pytest1.vst")
    model = _get_v1_dummy(fp)
    new_model = from_vst(fp)

    # assert hasattr(model, 'predict')
    # assert not hasattr(model, 'predictx')
    assert hasattr(model, "predict")
    assert hasattr(new_model, "predict")
    assert not hasattr(model, "predictx")
    assert not hasattr(new_model, "predictx")

    with pytest.raises(ValueError):
        to_vst(None, "...")


def test_simple_load():
    model, filename = simple_load("pytest0.vst")

    assert filename == "pytest0.vst"

    assert isinstance(model, SimpleTransformerProtocol)

    model, filename = simple_load(model)

    # filename is now name of the object:
    assert "object at" in filename

    assert isinstance(model, SimpleTransformerProtocol)

    with pytest.raises(TypeError):
        simple_load([model])


def test_load_advanced():
    # normal case
    with open("pytest1.vst", "rb") as f:
        model, metadata, valid_meta = _from_vst(f)
    assert isinstance(model, SimpleTransformerProtocol)
    assert metadata is None
    assert valid_meta

    # model + meta
    with open("pytest1.vst", "rb") as f:
        model, metadata, valid_meta = _from_vst(f, with_metadata=True)
    assert isinstance(model, SimpleTransformerProtocol)
    assert isinstance(metadata, Metadata)
    assert valid_meta

    # alternative notation:
    with open("pytest1.vst", "rb") as f:
        model, metadata, valid_meta = from_vst_with_metadata(f)
    assert isinstance(model, SimpleTransformerProtocol)
    assert isinstance(metadata, Metadata)
    assert valid_meta

    # meta only
    with open("pytest1.vst", "rb") as f:
        model, metadata, valid_meta = _from_vst(f, with_metadata=True, with_model=False)
    assert model is None
    assert isinstance(metadata, Metadata)
    assert valid_meta

    # nothing
    with open("pytest1.vst", "rb") as f:
        model, metadata, valid_meta = _from_vst(f, with_metadata=False, with_model=False)
    assert model is None
    assert metadata is None
    assert valid_meta

def test_loading_corrupted():
    file = _get_corrupted_vst(reason="pickling")

    with pytest.raises(CorruptedModelException):
        try:
            from_vst(
                file
            )
        except CorruptedModelException as e:
            assert e.reason == "pickling"
            raise e

    file = _get_corrupted_vst(reason="compression")

    with pytest.raises(CorruptedModelException):
        try:
            from_vst(
                file
            )
        except CorruptedModelException as e:
            print(e.origin)
            assert e.reason == "compression"
            raise e



def test_backwards_compat():
    fp = Path("pytest0.vst")

    model = _get_v0_dummy(fp)
    new_model = from_vst(fp)

    assert hasattr(new_model, "predict")
    assert not hasattr(new_model, "predictx")

    assert (
        new_model.predict("something")[0]
        == "gnihtemos"
        == model.predict("something")[0]
        == model.predict(["something"])[0][0]
    )


def test_upgrade():
    fp = Path("pytest0.vst")

    model = _get_v0_dummy(fp)

    upgraded = io.BytesIO()
    assert upgrade_metadata(fp, upgraded)

    with fp.open("rb") as f:
        _, metadata, valid_meta = _from_vst(f, with_model=False, with_metadata=True)

    assert not valid_meta

    new_model, metadata, valid_meta = from_vst_with_metadata(upgraded)

    assert valid_meta

    assert (
        new_model.predict("something")[0]
        == "gnihtemos"
        == model.predict("something")[0]
        == model.predict(["something"])[0][0]
    )

    assert not upgrade_metadata(upgraded, io.BytesIO())

def test_custom_excepthook(capsys):
    my_exception = ValueError("catch")
    custom_excepthook(ValueError, my_exception, None)
    captured = capsys.readouterr()

    assert "" in captured.out
    assert "ValueError:" in captured.err
    assert "catch" in captured.err