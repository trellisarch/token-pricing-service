import ast
import os
import glob

import pytest


DAG_DIRS = os.path.join(os.path.dirname(__file__), os.pardir, "dags")

LIB_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "lib")

MODELS_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "models")

CONFIG_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "config")


def _find_py_files(*dirs):
    """Find all Python files under the given directories, excluding __init__.py."""
    files = []
    for d in dirs:
        pattern = os.path.join(d, "**", "*.py")
        files.extend(
            f
            for f in glob.glob(pattern, recursive=True)
            if not f.endswith("__init__.py")
        )
    return files


all_py_files = _find_py_files(DAG_DIRS, LIB_DIR, MODELS_DIR, CONFIG_DIR)


@pytest.mark.parametrize(
    "py_file",
    all_py_files,
    ids=[
        os.path.relpath(f, os.path.join(os.path.dirname(__file__), os.pardir))
        for f in all_py_files
    ],
)
def test_python_file_parses(py_file):
    """Verify each Python file has valid syntax (catches SyntaxError, stray text, etc.)."""
    with open(py_file, "r") as f:
        source = f.read()
    try:
        ast.parse(source, filename=py_file)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {py_file}: {e}")
