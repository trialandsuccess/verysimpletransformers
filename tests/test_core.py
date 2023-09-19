import zlib
from pathlib import Path

import torch.cuda
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import pandas as pd
import logging
import dill

from src.verysimpletransformers.core import from_vst, to_vst, write_bundle
from src.verysimpletransformers.versioning import get_version
from src.verysimpletransformers.metadata_schema import MetaHeader, Metadata
from src.verysimpletransformers.types import DummyModel

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)


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

    assert new_model.predict("something") == "gnihtemos" == model.predict("something") == model.predict(["something"])[0]
