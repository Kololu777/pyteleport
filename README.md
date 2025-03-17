# Pyteleport

> [!IMPORTANT]
> This repository is a work in progress.
> This repository is planned to launch version 0.0.1 in April.

Pyteleport is library which, supports LLM and AI-Assisted-Programing. 

For example, you can merge files in a directory, into a single file. and you can pick up some files from a directory.


## Features

- Single file

- Pick up files


## Usage
Merge files from Multi-file to Single file.
```python
from pyteleport.singlefile import SingleFile
rule_fn = ""
SingleFile(path="./src", rule_fn= rule_fn)
```