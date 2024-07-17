# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.insert(
    0, str(root_path.absolute())
)  # Sphinxがライブラリを探索できるようにパスを追加


project = "AI-Notebook-backend"
copyright = "2024, OikawaPBL2024"
author = "OikawaPBL2024"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "myst_parser",
    "sphinx.ext.githubpages",
]


language = "ja"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# テーマを変更
html_theme = "sphinx_rtd_theme"

# Sphinxで扱うファイル形式を定義
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}
