# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The sphinx_html module includes functions to check whether the Sphinx
documentation exists or whether it needs to be created and a function to
generate the Sphinx html documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["check_sphinx_html_docs", "run_sphinx_html_build"]


import os

from qtpy import QtWidgets
from sphinx.cmd import build

from .get_documentation_targets import DOC_HOME_FILENAME, DOC_MAKE_DIRECTORY


def check_sphinx_html_docs(doc_dir=None):
    """
    Check whether the index.html file for the built sphinx documentation exists.

    Parameters
    ----------
    build_dir : Union[pathlib.Path, str, None], optional
        An optional build directory. If None, this defaults to the generic
        pydidas documentation directory. The default is None.

    Returns
    -------
    bool :
        Flag whether the Sphinx documentation exists or is being built. If
        either of these cases is true, the function will return True. Else,
        it will return a False which can trigger a call to build the
        documentation.
    """
    if doc_dir is None:
        _index_file = DOC_HOME_FILENAME
    else:
        _index_file = os.path.join(doc_dir, "index.html")
    return os.path.exists(_index_file)


def run_sphinx_html_build(build_dir=None, verbose=True):
    """
    Run the sphinx process to generate the html documentation.

    Parameters
    ----------
    build_dir : Union[pathlib.Path, str, None], optional
        An optional build directory. If None, this defaults to the generic
        pydidas documentation directory. The default is None.
    verbose : bool, optional
        Flag to control printing of a message. The default is True.
    """
    if build_dir is None:
        build_dir = os.path.join(DOC_MAKE_DIRECTORY, "build", "html")
    if verbose:
        print("=" * 60)
        print("-" * 60)
        print("----- The html documentation has not yet been created! -----")
        print("----- Running sphinx-build. This may take a bit.       -----")
        print("----- pydidas will automatically load once building of -----")
        print("----- the documentation has been finished.             -----")
        print("-" * 60)
        print("=" * 60)
        app = QtWidgets.QApplication.instance()
        for _widget in app.topLevelWidgets():
            if isinstance(_widget, QtWidgets.QSplashScreen) and hasattr(
                _widget, "show_aligned_message"
            ):
                _widget.show_aligned_message(
                    "Building html documentation (required only once during first "
                    "startup)"
                )
    build.main([os.path.join(DOC_MAKE_DIRECTORY, "source"), build_dir])
