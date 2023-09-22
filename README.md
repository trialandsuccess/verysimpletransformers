# Very Simple Transformers (VST)

<div align="center">
    <a href="https://pypi.org/project/verysimpletransformers"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/verysimpletransformers.svg"/></a>
    <a href="https://pypi.org/project/verysimpletransformers"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/verysimpletransformers.svg"/></a>
    <br/>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
    <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"/></a>
    <br/>
    <a href="https://github.com/trialandsuccess/verysimpletransformers/actions"><img alt="verysimpletransformers checks" src="https://github.com/trialandsuccess/verysimpletransformers/actions/workflows/su6.yml/badge.svg?branch=development"/></a>
    <a href="https://github.com/trialandsuccess/verysimpletransformers/actions"><img alt="Coverage" src="coverage.svg"/></a>
</div>

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [CLI](#cli)
- [Changelog](#changelog)
- [License](#license)

## Installation

## Usage

### Bundling

Bundling your machine learning model with VerySimpleTransformers is straightforward. Follow these steps:

Create or load your machine learning model (e.g., a ClassificationModel) using Simple Transformers.

Example:

```python
from simpletransformers.classification import ClassificationArgs, ClassificationModel

# Create a ClassificationModel
model_args = ClassificationArgs(
    num_train_epochs=1,
    overwrite_output_dir=True,
    save_model_every_epoch=False,
)

model = ClassificationModel(
    "bert",
    "bert-base-cased",  # or something like ./outputs
    args=model_args,
    use_cuda=True,
)
# optionally train on your data:
model.train_model(...)

```

Import the `verysimpletransformers` package, and use the `to_vst` function to package the model into a .vst file with
optional compression.

Provide the model, the output file path, and an optional compression level (0-9).
By default, compression will be disabled.

The output file path can be specified as:

- A string path (e.g., `"model.vst"`) for a standard file path.
- A `Path` object (e.g., `Path("model.vst")`) using `pathlib`.
- A binary I/O object (e.g., `BytesIO()`) for in-memory operations, if you don't want to save to a file.

Example:

```python
import verysimpletransformers  # or: from verysimpletransformers import to_vst
from pathlib import Path  # can be used instead of a string

verysimpletransformers.to_vst(model,
                              "my_model.vst",
                              compression=5,  # optional
                              )
```

Note: As an alias, `bundle_model` can be used instead of `to_vst`.

### Loading

Loading a machine learning model from a .vst file is just as simple. Follow these steps:

Import `from_vst` from `simpletransformers`.
Specify the path to the .vst file you want to load. Just like with `to_vst`, this path can be a `str`, `Path` or binary
IO.
Use the `from_vst` function to load the model. Optionally, you can specify the `device` parameter to set the device (
e.g., 'cpu' or 'cuda'). If not specified, the function will select a device based on availability.

Example:

```python
from verysimpletransformers import from_vst
from pathlib import Path

fp = Path("model.vst")  # can also be simply a string.

new_model = from_vst(fp,
                     device='cuda',  # optional
                     )

```

You can now use the `new_model` for various machine learning tasks.

Note: As an alias, `load_model` can be used instead of `to_vst`.

#### Additional Information

- The `.vst` files can be transferred and used across different devices, regardless of where the model was originally
  trained.

- Ensure that you have the required dependencies, such as SimpleTransformers and PyTorch, installed to use these
  functions effectively.

### Full Example

To see a full example of saving and loading a `.vst` file,
see [examples/basic.py](https://github.com/trialandsuccess/verysimpletransformers/tree/master/examples/basic.py)

## CLI

The VerySimpleTransformers CLI provides a convenient and versatile way to interact with and manage your machine learning
models created with VerySimpleTransformers. It allows you to perform various actions using a command-line interface,
making it easy to run, serve, and upgrade your models with ease.

### Usage

You can use the CLI with either `verysimpletransformers` or `vst` interchangeably. Here are some basic usage examples:

- Running a model interactively:
  ```shell
  verysimpletransformers model.vst
  vst model.vst
  ./model.vst
  ```

- Specifying an action when running:
  ```shell
  verysimpletransformers <action> model.vst
  verysimpletransformers model.vst <action>
  vst <action> model.vst
  vst model.vst <action>
  ./model.vst <action> # if the file has execution rights
  ```

### Available Actions

The following actions are available:

- **'run'**: Run the model interactively by typing prompts.

- **'serve'**: Start a simple HTTP server to serve model outputs. You can specify the following options:
    - `--port <PORT>`: Specify the port number (default: 8000).
    - `--host <HOST>`: Specify the host (default: 'localhost').

- **'upgrade'**: Upgrade the metadata of a model to the latest version.

### Example

Here's an example of starting a server for a classification model:

```shell
vst serve ./classification.vst
./classification.vst serve 
```

For more examples,
see [examples/basic.sh](https://github.com/trialandsuccess/verysimpletransformers/tree/master/examples/basic.sh)

### Notes

- A .vst file (e.g., 'model.vst') is required for most commands.
- You can specify `<action>`, which can be one of the available options mentioned above.
- If you leave `<action>` empty, a dropdown menu will appear for you to select from.
- You can use 'vst' or 'verysimpletransformers' interchangeably.

## About the .vst file format

The `.vst` file format is used to bundle machine learning models created with SimpleTransformers. Understanding its
structure is useful for working with these files effectively. The format consists of the following components:

- **Shebang Line**: The first line of the file is a shebang (`#!/usr/bin/env verysimpletransformers`) that allows the
  file to be executed using `./`. This line indicates that the file can be executed as a script.

- **Fixed Information (16 bytes)**:
    - `VST Protocol Version` (short, 2 bytes): Specifies the version of the VerySimpleTransformers Protocol used in the
      file. This allows for backwards compatibility with older versions of the file, which may have less metadata.
    - `Metadata Length` (short, 2 bytes): Indicates the length of the metadata section in bytes.
    - `Content Length` (long long, 8 bytes): Specifies the length of the content (actual model data) in bytes.

  **Explanation**: The total size of the fixed information is 12 bytes according to the data types (2 bytes
  for `short` + 2 bytes for `short` + 8 bytes for `long long`). However, it sums up to 16 bytes due to `struct` padding.
  The padding aligns the data structure to meet memory alignment requirements and ensure efficient memory access.

- **Metadata (Variable Length)**:
    - The next `Metadata Length` bytes contain the metadata, which can vary in length. The metadata is used to store
      information about the model and its compatibility with different versions of VerySimpleTransformers. The structure
      of the metadata can change between protocol versions.

    - Checks are performed on this metadata to ensure compatibility and integrity. If the metadata is invalid or belongs
      to a newer protocol version, a warning is issued, and the loading process continues.

- **Model Content (Variable Length)**:
    - The remaining bytes, equal to `Content Length`, contain the serialized model data. This is the actual (possibly
      compressed) machine learning model that was bundled into the `.vst` file.
    - The model contents are stored (and loaded) using `dill` (which is an extension of `pickle`).

```


                              ┌───────────────────────────────────────┐
                              │#!/usr/bin/env verysimpletransformers\n├──────────► Shebang
                              ├───┬───┬───────────┬───────────────────┤
                              │   │   │           │                   │
                              │2b │2b │  4 bytes  │  content length   │
              .vst version  ◄─┼── │   │           │       (n2)        ├──────────► 16 bytes
                              │   │   │ (padding) │                   │
    meta header length (n1) ◄─┼───┼── │           │      8 bytes      │
                              │   │   │           │                   │
                              ├───┴───┴───────────┴───────────────────┤
                              │                                       │
                              │                                       │
                              │                                       │
                              │              Meta Header              │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                n1 bytes               │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              ├───────────────────────────────────────┤
                              │                                       │
                              │                                       │
                              │         (possible compressed)         │
                              │                                       │
                              │                                       │
                              │      Machine Learning Model Dill      │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │               n2 bytes                │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │                                       │
                              │            ..............             │
                              │                                       │
                              └───────────────────────────────────────┘


```

## License

`verysimpletransformers` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

See `CHANGELOG.md` [on GitHub](https://github.com/trialandsuccess/verysimpletransformers/blob/master/CHANGELOG.md)
