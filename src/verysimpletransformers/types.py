"""
Mostly for mypy (and pytest).
"""

import typing

import numpy
import numpy as np
import numpy.typing as npt


class DummyModel:
    """
    Replacement for actual (big) ML model, useful for pytesting.
    """

    device = "cpu"

    @typing.overload
    def predict(self, target: str, **__: typing.Any) -> tuple[str, None]:  # pragma: no cover
        """
        If you enter a single input, you get a single output.
        """

    @typing.overload
    def predict(self, target: list[str], **__: typing.Any) -> tuple[list[str], None]:  # pragma: no cover
        """
        If you enter a list of inputs, you get a list of outputs.
        """

    def predict(self, target: str | list[str], **__: typing.Any) -> tuple[str | list[str], None]:
        """
        Simulate a machine learning response by just returning a reversed echo of the input.
        """
        if isinstance(target, list):
            return [self.predict(_)[0] for _ in target], None

        return target[::-1], None


if typing.TYPE_CHECKING:  # pragma: no cover
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
        | DummyModel
    )


@typing.runtime_checkable
class SimpleTransformerProtocol(typing.Protocol):
    """
    Defines the structue of a simple transformer model.

    This can be used to test isinstance without actually importing simpletransformers.
    """

    device: str

    def predict(self, to_predict: list[str]) -> tuple[list[str] | npt.NDArray[numpy.int32], npt.NDArray[np.float64]]:
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

    # real models have more of course, but these are the properties expected by our code.
