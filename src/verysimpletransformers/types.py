"""
Mostly for mypy (and pytest).
"""
from __future__ import annotations

import os
import sys
import typing

import numpy as np

if typing.TYPE_CHECKING:  # pragma: no cover
    import numpy.typing as npt
    from simpletransformers.classification import (
        ClassificationModel,
        MultiLabelClassificationModel,
        MultiModalClassificationModel,
    )
    from simpletransformers.conv_ai import ConvAIModel
    from simpletransformers.language_generation import LanguageGenerationModel
    from simpletransformers.language_modeling import LanguageModelingModel
    from simpletransformers.language_representation import RepresentationModel
    from simpletransformers.ner import NERModel
    from simpletransformers.question_answering import QuestionAnsweringModel
    from simpletransformers.retrieval import RetrievalModel
    from simpletransformers.seq2seq import Seq2SeqModel
    from simpletransformers.t5 import T5Model
    from torch.optim.lr_scheduler import LRScheduler
    from transformers import Adafactor, PreTrainedModel

    AllClassificationModels = ClassificationModel | MultiLabelClassificationModel | MultiModalClassificationModel

    AllSimpletransformersModels = (
        AllClassificationModels
        | ConvAIModel
        | LanguageGenerationModel
        | LanguageModelingModel
        | RepresentationModel
        | NERModel
        | QuestionAnsweringModel
        | RetrievalModel
        | Seq2SeqModel
        | T5Model
        | "DummyModel"
    )


class DummyModel:
    """
    Replacement for actual (big) ML model, useful for pytesting.
    """

    device = "cpu"
    model = None

    def predict(self, to_predict: list[str]) -> tuple[list[str] | npt.NDArray[np.int32], npt.NDArray[np.float64]]:
        """
        Dummy 'predict' just reverses the string for each input.
        """
        return [_[::-1] for _ in to_predict], np.ndarray(0)

    def save_model(
        self,
        output_dir: str = None,
        optimizer: Adafactor = None,
        scheduler: LRScheduler = None,
        model: PreTrainedModel = None,
        results: dict[str, typing.Any] = None,
    ) -> None:
        """
        Dummy model has nothing to save, so just print.
        """
        print("Dummy model has no files; Saving empty files to disk.", file=sys.stderr)
        output_dir = output_dir or "outputs/"
        print(f"{output_dir=}; {optimizer=}; {scheduler=}; {model=}; {self.model=}; {results=}", file=sys.stderr)

        expected_files = [
            "config.json",
            "model_args.json",
            "pytorch_model.bin",
            "special_tokens_map.json",
            "tokenizer_config.json",
            "tokenizer.json",
            "training_args.bin",
            "vocab.txt",
        ]

        os.system(f"mkdir {output_dir}; " f"cd {output_dir}; " f"touch {' '.join(expected_files)}")  # nosec


@typing.runtime_checkable
class SimpleTransformerProtocol(typing.Protocol):
    """
    Defines the structue of a simple transformer model.

    This can be used to test isinstance without actually importing simpletransformers.
    """

    device: str
    model: PreTrainedModel  # internal huggingface.transformers model

    def predict(self, to_predict: list[str]) -> tuple[list[str] | npt.NDArray[np.int32], npt.NDArray[np.float64]]:
        """
        Simple Transformers have a predict function that calls a trained model on some inputs.

        It returns a tuple with 2 parts:

        1.
        If the model has labeled outputs, a list of strings will be returned.
        If the labels are unlabeled, a numpy array of ints will be returned.
        With .tolist() this can be transformed to a normal list.

        2.
        Additionally, a nested numpy array of floats is returned containing the predictions for each label:
        E.g. for 2 inputs and 3 labels:
        array([[-1.06826222, -2.81530643,  4.42381239], [-1.54674757, -2.70588231,  4.82942677]]))
        """

    def save_model(
        self,
        output_dir: str = None,
        optimizer: Adafactor = None,
        scheduler: LRScheduler = None,
        model: PreTrainedModel = None,
        results: dict[str, typing.Any] = None,
    ) -> None:
        """
        Save a model from memory back to disk.
        """

    # real models have more of course, but these are the properties expected by our code.
