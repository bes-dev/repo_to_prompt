#!/usr/bin/env python3
"""
Copyright 2025 by Sergei Belousov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import logging
import os
import subprocess
import sys
import tempfile

from repo_to_prompt.folder_parser import FolderParser


def main() -> None:
    """Main function for the CLI tool."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(
        description=(
            "CLI for repo to prompt converter. The path can be a local directory "
            "or a git repository URL."
        )
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help=(
            "Path to the repository to convert. Can be a local directory "
            "or a git repository URL."
        ),
    )
    parser.add_argument(
        "--interfaces-only",
        action="store_true",
        help="Extract only interfaces (without implementation) for all *.py files.",
    )
    args = parser.parse_args()

    # Determine if the provided path is a local directory or a git repository URL.
    if os.path.isdir(args.path):
        repo_path = args.path
        folder_parser = FolderParser(repo_path, interfaces_only=args.interfaces_only)
        print(folder_parser.dump_to_string())
    else:
        # Clone the git repository into a temporary directory.
        with tempfile.TemporaryDirectory() as temp_dir:
            logging.info(
                f"Cloning git repository {args.path} to temporary directory {temp_dir}..."
            )
            clone_cmd = ["git", "clone", args.path, temp_dir]
            result = subprocess.run(
                clone_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode != 0:
                logging.error(f"Git clone failed: {result.stderr}")
                sys.exit(1)
            folder_parser = FolderParser(temp_dir, interfaces_only=args.interfaces_only)
            print(folder_parser.dump_to_string())
            # The temporary directory is automatically removed here.


if __name__ == "__main__":
    main()
