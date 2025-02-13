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

import logging
import os
import sys

from pathspec import PathSpec


class IgnoreSpec:
    """
    Handles ignore specifications based on .gitignore and .dixieignore files.
    """

    def __init__(self, root_folder: str) -> None:
        """
        Initialize with the root folder and read ignore files.

        Args:
            root_folder (str): The root directory path.
        """
        self.root_folder = root_folder
        self.spec = self._read_ignore_files()

    def _read_ignore_files(self) -> PathSpec:
        """
        Read and compile ignore patterns from .gitignore and .dixieignore files.

        Returns:
            PathSpec: Compiled ignore patterns.
        """
        ignore_files = [".gitignore", ".dixieignore"]
        patterns = []
        for ignore_file in ignore_files:
            ignore_file_path = os.path.join(self.root_folder, ignore_file)
            if os.path.exists(ignore_file_path):
                with open(ignore_file_path, "r", encoding="utf-8") as f:
                    patterns.extend(f.read().splitlines())
        return PathSpec.from_lines("gitwildmatch", patterns)

    def is_ignored(self, path: str, is_dir: bool = False) -> bool:
        """
        Determine if a given path should be ignored.

        Args:
            path (str): The file or directory path to check.
            is_dir (bool, optional): True if the path is a directory. Defaults to False.

        Returns:
            bool: True if the path is ignored, False otherwise.
        """
        rel_path = os.path.relpath(path, self.root_folder)
        if is_dir:
            rel_path += "/"
        return self.spec.match_file(rel_path)


class LanguageSpecifier:
    """
    Specifies programming languages based on file extensions.
    """

    LANGUAGE_MAP = {
        ".py": "python",
        ".json": "json",
        ".js": "javascript",
        ".ts": "typescript",
        ".html": "html",
        ".css": "css",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".go": "go",
        ".rs": "rust",
        ".sh": "bash",
        ".bat": "batch",
        ".ps1": "powershell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xml": "xml",
        ".md": "markdown",
        ".txt": "text",
    }

    @classmethod
    def get_language(cls, filename: str) -> str:
        """
        Get the programming language for a given filename based on its extension.

        Args:
            filename (str): The file name.

        Returns:
            str: The corresponding language, or an empty string if not found.
        """
        extension = os.path.splitext(filename)[1].lower()
        return cls.LANGUAGE_MAP.get(extension, "")


class DirectoryTree:
    """
    Represents the directory tree structure, excluding ignored paths.
    """

    def __init__(self, root_folder: str, ignore_spec: IgnoreSpec) -> None:
        """
        Initialize with the root folder and ignore specifications.

        Args:
            root_folder (str): The root directory path.
            ignore_spec (IgnoreSpec): Instance used to determine ignored paths.
        """
        self.root_folder = root_folder
        self.ignore_spec = ignore_spec
        self.tree_lines = [os.path.basename(root_folder) + "/"]
        self.source_files = []

    def build_tree(self) -> None:
        """
        Build the directory tree by traversing the file system.
        """
        self._traverse(self.root_folder, "")

    def _traverse(self, current_path: str, prefix: str) -> None:
        """
        Recursively traverse directories to build the tree structure.

        Args:
            current_path (str): The current directory path.
            prefix (str): The prefix string for formatting the tree.
        """
        entries = sorted(os.listdir(current_path))
        entries_to_keep = []
        for entry in entries:
            entry_path = os.path.join(current_path, entry)
            if self._should_exclude(entry_path):
                continue
            entries_to_keep.append(entry)
        entries_count = len(entries_to_keep)
        for idx, entry in enumerate(entries_to_keep):
            entry_path = os.path.join(current_path, entry)
            rel_entry = os.path.relpath(entry_path, self.root_folder)
            is_last = idx == entries_count - 1
            connector = "`-- " if is_last else "|-- "
            new_prefix = prefix + ("    " if is_last else "|   ")
            self.tree_lines.append(prefix + connector + entry)
            if os.path.isdir(entry_path):
                self._traverse(entry_path, new_prefix)
            else:
                self.source_files.append((rel_entry, entry_path))

    def _should_exclude(self, entry_path: str) -> bool:
        """
        Determine whether to exclude a given path based on ignore specifications.

        Args:
            entry_path (str): The path to check.

        Returns:
            bool: True if the path should be excluded, False otherwise.
        """
        if os.path.isdir(entry_path):
            return self.ignore_spec.is_ignored(entry_path, is_dir=True)
        return self.ignore_spec.is_ignored(entry_path)


class FolderParser:
    """
    Parses a folder structure into a dictionary with file details and a folder tree.
    """

    def __init__(self, root_folder: str, interfaces_only: bool = False) -> None:
        """
        Initialize the FolderParser.

        Args:
            root_folder (str): Path to the root folder.
            interfaces_only (bool, optional): If True, extract only interfaces for .py files.
        """
        self.root_folder = root_folder
        self.interfaces_only = interfaces_only
        self.parsed_files = {}
        self.folder_tree = []
        self._parse()

    def _parse(self) -> None:
        """
        Parse the folder structure.
        """
        ignore_spec = IgnoreSpec(self.root_folder)
        directory_tree = DirectoryTree(self.root_folder, ignore_spec)
        directory_tree.build_tree()
        self.folder_tree = directory_tree.tree_lines
        self._parse_files(directory_tree.source_files)

    def _parse_files(self, source_files: list) -> None:
        """
        Parse files from the source list.

        Args:
            source_files (list): List of tuples (relative_path, full_path).
        """
        from repo_to_prompt.extract_interfaces import extract_interfaces

        language_specifier = LanguageSpecifier()
        for rel_path, full_path in source_files:
            file_text = self._read_file(full_path)
            file_type = language_specifier.get_language(full_path)
            if self.interfaces_only and file_type == "python":
                interfaces_code = extract_interfaces(file_text)
                logging.info(f"Extracted interfaces for {rel_path}:\n{interfaces_code}")
                file_text = interfaces_code
            self.parsed_files[rel_path] = {"text": file_text, "type": file_type}

    @staticmethod
    def _read_file(path: str) -> str:
        """
        Read the content of a file.

        Args:
            path (str): The file path.

        Returns:
            str: File content or an error message if reading fails.
        """
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return "[Error reading file]"

    def dump_to_string(self) -> str:
        """
        Dump the parsed folder structure to a formatted string.

        Returns:
            str: A string containing the folder tree and file sources.
        """
        output = ["* Folder tree *\n"] + self.folder_tree + ["\n", "* Sources *\n"]
        root_folder_name = os.path.basename(self.root_folder)
        for file_path, file_info in self.parsed_files.items():
            output.extend(
                [
                    f"** FILE: {root_folder_name}/{file_path} **",
                    f"```{file_info['type']}",
                    file_info["text"],
                    "```\n",
                ]
            )
        return "\n".join(output)

    def dump_file_to_string(self, file_path: str) -> str:
        """
        Dump a specific file to a formatted string.

        Args:
            file_path (str): The relative file path.

        Returns:
            str: A formatted string for the file, or an empty string if not found.
        """
        root_folder_name = os.path.basename(self.root_folder)
        if file_path in self.parsed_files:
            file_info = self.parsed_files[file_path]
            return "\n".join(
                [
                    f"** FILE: {root_folder_name}/{file_path} **",
                    f"```{file_info['type']}",
                    file_info["text"],
                    "```\n",
                ]
            )
        return ""

    def get_all_paths(self) -> list:
        """
        Get all file paths in the parsed folder structure.

        Returns:
            list: A list of relative file paths.
        """
        return list(self.parsed_files.keys())


def main() -> None:
    """
    Main function to run the FolderParser.
    Usage:
        python folder_parser.py <root_folder>
    """
    root_folder = sys.argv[1] if len(sys.argv) > 1 else "."
    folder_parser = FolderParser(root_folder)
    print(folder_parser.dump_to_string())
    # print(folder_parser.get_all_paths())


if __name__ == "__main__":
    main()
