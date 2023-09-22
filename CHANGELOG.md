# Changelog

<!--next-version-placeholder-->

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
