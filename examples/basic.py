from verysimpletransformers import from_vst, to_vst

########################################
### From the SimpleTransformers docs ###
########################################

from simpletransformers.classification import ClassificationModel, ClassificationArgs
import pandas as pd
import logging
import torch

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

# Optional model configuration
model_args = ClassificationArgs(num_train_epochs=1)

# Create a ClassificationModel
model = ClassificationModel(
    "roberta",
    "roberta-base",
    args=model_args,
    use_cuda=torch.cuda.is_available()
)

# Train the model
model.train_model(train_df)

# Evaluate the model
result, model_outputs, wrong_predictions = model.eval_model(eval_df)

# Make predictions with the model
predictions, raw_outputs = model.predict(["Sam was a Wizard"])

print("Model Prediction:", predictions[0])

######################################
### Now let's package it into VST! ###
######################################

to_vst(model, "example_basic.vst", compression=5)

# that's it!

######################################
### Now let's load the model again ###
######################################

model = from_vst("example_basic.vst")

# that's it!
predictions, _ = model.predict(["Sam was a Wizard"])

print("New Model Prediction:", predictions[0])
