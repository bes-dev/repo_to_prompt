# repo_to_prompt

## Overview

`repo_to_prompt` is a Python package that provides utilities for parsing a repository's file structure and source code into a formatted prompt. It can extract full file contents or only interface definitions from Python files. This tool is useful for generating structured representations of codebases, assisting in AI-powered code understanding, documentation, and summarization.

## Features

- Parse a repository (local directory or remote Git repository) into a structured prompt.
- Extract and format folder tree structures.
- Process multiple file types, identifying their language based on extensions.
- Extract only interface definitions (classes, functions, and type annotations) from Python source files.
- Support `.gitignore` and `.dixieignore` files to exclude specific files and directories.
- Command-line interface (CLI) for easy usage.

## Installation

To install the package, clone the repository and install dependencies:

```sh
# Clone the repository
$ git clone https://github.com/your-repo/repo_to_prompt.git

# Navigate to the directory
$ cd repo_to_prompt

# Install dependencies
$ pip install -r requirements.txt
```

Alternatively, you can install it as a package:

```sh
$ pip install repo_to_prompt
```

## Usage

### Command-Line Interface

You can use the `repo_to_prompt` CLI to generate a structured prompt from a local directory or a Git repository.

#### Basic Usage

```sh
$ python -m repo_to_prompt.cli --path <path-to-repo>
```

#### Extract Only Interfaces

To extract only class and function signatures from Python files:

```sh
$ python -m repo_to_prompt.cli --path <path-to-repo> --interfaces-only
```

#### Parsing a Git Repository

If the provided path is a Git repository URL, it will be cloned into a temporary directory before processing:

```sh
$ python -m repo_to_prompt.cli --path https://github.com/user/repo.git
```

## Module Descriptions

### `repo_to_prompt/cli.py`

- Provides a command-line interface.
- Accepts a repository path (local or remote Git repository).
- Calls `FolderParser` to generate a structured prompt.

### `repo_to_prompt/folder_parser.py`

- Parses a folder structure, extracting file content and metadata.
- Uses `IgnoreSpec` to respect `.gitignore` and `.dixieignore` rules.
- Builds a formatted tree representation of the repository.
- Calls `extract_interfaces.py` if the `--interfaces-only` flag is enabled.

### `repo_to_prompt/extract_interfaces.py`

- Parses Python source files using the AST (Abstract Syntax Tree).
- Extracts class and function signatures, along with docstrings.
- Removes implementation details to create an interface-only representation.

### `repo_to_prompt/__init__.py`

- Initializes the `repo_to_prompt` package.

## Example Output

When running `repo_to_prompt` on a sample project, the output follows this structure:

```text
* Folder tree *

repo/
|-- main.py
|-- utils.py
|-- config/
|   |-- settings.py
`-- README.md

* Sources *

** FILE: repo/main.py **
```python
import os

def hello():
    """Prints a greeting message."""
    print("Hello, world!")
```
```

If `--interfaces-only` is specified:

```text
** FILE: repo/main.py **
```python
def hello():
    """Prints a greeting message."""
```
```

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.

## Author

Created by **Sergei Belousov**.
