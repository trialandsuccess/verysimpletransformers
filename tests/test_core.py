import torch.cuda
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import pandas as pd
import logging

from src.verysimpletransformers.core import bundle

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)

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


def test_bundle():
    # Optional model configuration
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

    bundle(model, "pytest1.vst", compression=3)
