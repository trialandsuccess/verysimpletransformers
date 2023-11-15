# Changelog

<!--next-version-placeholder-->

## v0.4.0 (2023-11-15)

### Feature

* Add `cache` to from_drive to prevent re-downloading files that exist locally ([`6bf1135`](https://github.com/trialandsuccess/verysimpletransformers/commit/6bf1135797509413679dae632e9c38875fb57208))

## v0.3.5 (2023-11-15)

### Fix

* Require at least drive-in 0.1.4 with deals with new requests json exception ([`df81a7a`](https://github.com/trialandsuccess/verysimpletransformers/commit/df81a7a9fe4a3e8545673d538b753eb924e5d3bb))

## v0.3.4 (2023-11-15)

### Fix

* Add simple repr to metadata ([`dbf3c96`](https://github.com/trialandsuccess/verysimpletransformers/commit/dbf3c9673f76e378fca801d36b72c3ae1d48796e))
* Bump configuraptor (with typeguard) version requirement ([`458d8cd`](https://github.com/trialandsuccess/verysimpletransformers/commit/458d8cd187ef74326e86e2f088a762eee70e5adf))

## v0.3.3 (2023-10-07)

### Fix

* **cli:** Use readline to enable history in interactive mode ([`b5fac56`](https://github.com/trialandsuccess/verysimpletransformers/commit/b5fac56e068234e2d617ad2c45f63e47177e9317))

## v0.3.2 (2023-10-02)

### Fix

* **cli:** Minor tweaks and improvements to run, serve and stdin ([`d5f3035`](https://github.com/trialandsuccess/verysimpletransformers/commit/d5f3035d966933380739a11d90431dd520ec4e8d))

## v0.3.1 (2023-10-02)

### Fix

* **cli:** Interactive run only returned the  first character for seq2seq ([`3fb5b27`](https://github.com/trialandsuccess/verysimpletransformers/commit/3fb5b277389cfd6697bc0e584e4d07b837e3d377))
* **cli:** Add plumbum as dependency ([`ead5ade`](https://github.com/trialandsuccess/verysimpletransformers/commit/ead5aded817c20fd9f7605ecfaa4abc137a36097))

## v0.3.0 (2023-10-02)

### Feature

* Add save_to_disk to transform a .vst file back into the original model files ([`8b4497c`](https://github.com/trialandsuccess/verysimpletransformers/commit/8b4497c7b5eedf50bb421b1557de9a5b246c9f4a))

## v0.2.0 (2023-09-28)

### Feature

* Added `drive` extra via `drive-in` library ([`634e250`](https://github.com/trialandsuccess/verysimpletransformers/commit/634e250690c091c5b527b9fd4bd9bcc660c5e88c))
* **drive:** WIP to also add Drive Downloads (directly back to into a model) ([`e89b727`](https://github.com/trialandsuccess/verysimpletransformers/commit/e89b72762c4d76f4ca1f9442317d47a03517051c))
* **drive:** Add simple google drive api to store models ([`cf37a27`](https://github.com/trialandsuccess/verysimpletransformers/commit/cf37a271e17a479a2482d9a325a8beed6aa38a6c))

## v0.1.2 (2023-09-22)

### Documentation

* Set badges to absolute url so they work on pypi ([`f427b96`](https://github.com/trialandsuccess/verysimpletransformers/commit/f427b9629cae22de22c12ac53c0a1acb1c02e9aa))

## v0.1.1 (2023-09-22)

### Fix

* **device:** Model.device may not be a string, so convert it. Also enable compression by default. ([`d609584`](https://github.com/trialandsuccess/verysimpletransformers/commit/d609584abd384064388d20a1ae5650d5ca05800b))

### Documentation

* **badge:** Fix su6 checks badge in readme ([`4d325cf`](https://github.com/trialandsuccess/verysimpletransformers/commit/4d325cf2ccf271bb896b650a15643efc5aa422fc))

## v0.1.0 (2023-09-22)

### Feature

* **cli:** Improved Model Loading and Metadata Handling ([`56f6070`](https://github.com/trialandsuccess/verysimpletransformers/commit/56f6070ef8031eeff5f563b39b5132bd40e91dbe))
* **cli:** Made run and serve work, overall better cli ([`c8a2829`](https://github.com/trialandsuccess/verysimpletransformers/commit/c8a2829131f1544fcad0c31ca94e8d7ffe2ada70))
* **cli:** Started on `vst serve model.vst` command ([`f69c297`](https://github.com/trialandsuccess/verysimpletransformers/commit/f69c29702c2fe4a99240c3ceed92b75cf607fe7c))
* **meta:** Added metadata checks on load ([`0f56f88`](https://github.com/trialandsuccess/verysimpletransformers/commit/0f56f88126ce94ae0ef3fa3395874d1f17d7338b))

### Documentation

* **examples:** Updated example directory and README ([`713aec7`](https://github.com/trialandsuccess/verysimpletransformers/commit/713aec7654540f84ffd803c81ad889779e8dc088))
* Updated README, WIP to make more pytests + coverage (although that's hard for the interactive cli part) ([`dd840b6`](https://github.com/trialandsuccess/verysimpletransformers/commit/dd840b6be7a6f045203b30fd79021beae8fe9f64))

## v0.1.0-beta.3 (2023-09-20)

### Feature

* **pickle:** Allow choosing a device (cpu or cuda) ([`186d15c`](https://github.com/trialandsuccess/verysimpletransformers/commit/186d15c88cee2c99d45f1bee3b743d2210be58f1))

## v0.1.0-beta.2 (2023-09-19)

### Fix

* When going from CUDA to CPU, it shouldn't crash anymore ([`9253aec`](https://github.com/trialandsuccess/verysimpletransformers/commit/9253aec866cea3f1480cce5a7c99435eeffd22c6))

## v0.1.0-beta.1 (2023-09-19)

### Feature

* Started versioning the metadata for backwards compatibility ([`d93dfa5`](https://github.com/trialandsuccess/verysimpletransformers/commit/d93dfa5005db9730bc3a83b722178b92302ad352))
* Initial commit ([`954ca9e`](https://github.com/trialandsuccess/verysimpletransformers/commit/954ca9ea57e73d1d6ff5c5d01b8e34446e1bd8b4))

### Fix

* **cli:** --version works again ([`304ea54`](https://github.com/trialandsuccess/verysimpletransformers/commit/304ea542f0fb6233cad2db09192027793b24bf31))
