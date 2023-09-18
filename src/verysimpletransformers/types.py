import typing

if typing.TYPE_CHECKING:
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
    )
