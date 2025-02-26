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

from setuptools import setup, find_packages

setup(
    name='repo_to_prompt',
    version='0.1.0',
    description='A tool to convert repo to prompt',
    author='Sergei Belousov aka BeS',
    author_email='sergei.o.belousov@gmail.com',
    url='https://github.com/bes-dev/repo_to_prompt.git',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=[".git", ".gitignore"]),
    install_requires=[
        'pathspec'
    ],
    entry_points={
        'console_scripts': [
            'repo_to_prompt = repo_to_prompt.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
