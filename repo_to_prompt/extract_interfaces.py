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

import ast
import textwrap


def extract_interfaces(code: str) -> str:
    """
    Extract class and function declarations (including methods), annotated fields,
    docstrings, and comments (if applicable) from Python code without including the
    implementation bodies. Returns a string with these declarations.
    """
    # Parse the source code into an AST.
    tree = ast.parse(code)
    INDENT = " " * 4  # Standard indent (4 spaces)
    lines = []  # List of lines to build the result

    def get_docstring(node) -> str:
        """Return the raw docstring from the node or an empty string."""
        raw = ast.get_docstring(node, clean=False)
        return raw if raw else ""

    def format_docstring(docstring: str, indent_level: int) -> str:
        """
        Format the docstring with proper indentation.
        """
        if not docstring:
            return ""
        dedented = textwrap.dedent(docstring)
        indent = INDENT * indent_level
        return f'{indent}"""\n' + textwrap.indent(dedented, indent) + "\n" + indent + '"""'

    def format_decorators(node: ast.AST, indent_level: int) -> str:
        """
        Return a string of decorators for a class/function/method.
        """
        if not hasattr(node, "decorator_list") or not node.decorator_list:
            return ""
        decorators = []
        indent = INDENT * indent_level
        for decorator in node.decorator_list:
            dec_str = ast.unparse(decorator).strip()
            decorators.append(f"{indent}@{dec_str}")
        return "\n".join(decorators)

    def format_function_signature(func_node: ast.FunctionDef, indent_level: int) -> str:
        """
        Format the function signature (e.g., 'def name(args):') preserving annotations.
        """
        indent = INDENT * indent_level
        # Preserve only the docstring (if present) and remove other implementations.
        body_copy = list(func_node.body)
        new_body = []
        if (
            body_copy
            and isinstance(body_copy[0], ast.Expr)
            and isinstance(body_copy[0].value, ast.Constant)
            and isinstance(body_copy[0].value.value, str)
        ):
            new_body = [body_copy[0]]
        func_node.body = new_body

        func_str = ast.unparse(func_node)
        # Remove any docstring block from the unparsed output.
        func_lines = func_str.splitlines()
        new_lines = []
        in_docstring = False
        for line in func_lines:
            if line.strip().startswith('"""') and not in_docstring:
                in_docstring = True
                continue
            if in_docstring:
                if line.strip().endswith('"""'):
                    in_docstring = False
                continue
            new_lines.append(line)
        signature_line = new_lines[0].strip()
        if not signature_line.endswith(":"):
            signature_line += ":"
        return f"{indent}{signature_line}"

    def format_class_signature(class_node: ast.ClassDef, indent_level: int) -> str:
        """
        Format the class signature (e.g., 'class MyClass(Base1, Base2):').
        """
        indent = INDENT * indent_level
        bases_str = ""
        if class_node.bases:
            bases = [ast.unparse(base) for base in class_node.bases]
            bases_str = "(" + ", ".join(bases) + ")"
        return f"{indent}class {class_node.name}{bases_str}:"

    def process_body(nodes, indent_level: int) -> None:
        """
        Process a list of AST nodes (class body or module-level) and extract declarations.
        """
        for node in nodes:
            if isinstance(node, ast.AnnAssign):
                # Process annotated fields (e.g., "title: str" or "title: str = value")
                target_code = ast.unparse(node.target)
                ann_code = ast.unparse(node.annotation)
                if node.value is not None:
                    value_code = ast.unparse(node.value)
                    line = f"{INDENT * indent_level}{target_code}: {ann_code} = {value_code}"
                else:
                    line = f"{INDENT * indent_level}{target_code}: {ann_code}"
                lines.append(line)
            elif isinstance(node, ast.ClassDef):
                decorators = format_decorators(node, indent_level)
                if decorators:
                    lines.append(decorators)
                lines.append(format_class_signature(node, indent_level))
                class_doc = get_docstring(node)
                if class_doc:
                    lines.append(format_docstring(class_doc, indent_level + 1))
                process_body(node.body, indent_level + 1)
            elif isinstance(node, ast.FunctionDef):
                decorators = format_decorators(node, indent_level)
                if decorators:
                    lines.append(decorators)
                lines.append(format_function_signature(node, indent_level))
                func_doc = get_docstring(node)
                if func_doc:
                    lines.append(format_docstring(func_doc, indent_level + 1))
            else:
                # Skip other node types.
                continue

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            decorators = format_decorators(node, 0)
            if decorators:
                lines.append(decorators)
            lines.append(format_class_signature(node, 0))
            class_doc = get_docstring(node)
            if class_doc:
                lines.append(format_docstring(class_doc, 1))
            process_body(node.body, 1)
        elif isinstance(node, ast.FunctionDef):
            decorators = format_decorators(node, 0)
            if decorators:
                lines.append(decorators)
            lines.append(format_function_signature(node, 0))
            func_doc = get_docstring(node)
            if func_doc:
                lines.append(format_docstring(func_doc, 1))
        else:
            continue

    return "\n".join(lines)
