# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import copy
import unittest
import sys

from pydidas.apps.app_parsers import (
    parse_composite_creator_cmdline_arguments,
    parse_execute_workflow_cmdline_arguments)
from pydidas.core.utils import get_random_string

class TestAppParsers(unittest.TestCase):

    def setUp(self):
        self._argv = copy.copy(sys.argv)

    def tearDown(self):
        sys.argv = self._argv

    def test_parse_composite_creator_cmdline_arguments(self):
        sys.argv = ['test', '-file_stepping', '5', '-binning', '2',
                    '-first_file', 'testname']
        parsed = parse_composite_creator_cmdline_arguments()
        self.assertEqual(parsed['file_stepping'], 5)
        self.assertEqual(parsed['binning'], 2)
        self.assertEqual(parsed['first_file'], 'testname')

    def test_parse_execute_workflow_cmdline_arguments_no_args(self):
        sys.argv = ['test']
        parsed = parse_execute_workflow_cmdline_arguments()
        self.assertFalse(parsed['autosave'])
        self.assertIsNone(parsed['autosave_dir'])
        self.assertIsNone(parsed['autosave_format'])

    def test_parse_execute_workflow_cmdline_arguments(self):
        _dir = get_random_string(12)
        _format = ':.3f'
        sys.argv = ['test', '--autosave', '-d', _dir, '-f', _format]
        parsed = parse_execute_workflow_cmdline_arguments()
        self.assertTrue(parsed['autosave'])
        self.assertEqual(parsed['autosave_dir'], _dir)
        self.assertEqual(parsed['autosave_format'], _format)



if __name__ == "__main__":
    unittest.main()
