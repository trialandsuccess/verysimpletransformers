"""
Mostly for mypy (and pytest).
"""

import typing


class DummyModel:
    """
    Replacement for actual (big) ML model, useful for pytesting.
    """

    @typing.overload
    def predict(self, target: str, **__: typing.Any) -> str:  # pragma: no cover
        """
        If you enter a single input, you get a single output.
        """

    @typing.overload
    def predict(self, target: list[str], **__: typing.Any) -> list[str]:  # pragma: no cover
        """
        If you enter a list of inputs, you get a list of outputs.
        """

    def predict(self, target: str | list[str], **__: typing.Any) -> str | list[str]:
        """
        Simulate a machine learning response by just returning a reversed echo of the input.
        """
        if isinstance(target, list):
            return [self.predict(_) for _ in target]

        return target[::-1]


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
