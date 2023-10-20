"""Basic tests that do not require Django."""
import os
import unittest

import toml

from nautobot_device_lifecycle_mgmt import __version__ as project_version


class TestVersion(unittest.TestCase):
    """Test Version is the same."""

    def test_version(self):
        """Verify that pyproject.toml version is same as version specified in the package."""
        parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        poetry_version = toml.load(os.path.join(parent_path, "pyproject.toml"))["tool"]["poetry"]["version"]
        self.assertEqual(project_version, poetry_version)
