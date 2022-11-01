import os
import unittest

import pytest

from askanna.core.utils.file import get_files_in_dir, get_files_in_paths


@pytest.fixture(autouse=True)
def change_dir():
    cwd = os.getcwd()
    yield
    os.chdir(cwd)


class TestGetFiles(unittest.TestCase):
    def test_get_files_dir_simple(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)

        files = get_files_in_dir(".")
        self.assertEqual(len(files), 3)
        self.assertTrue("askanna.yml" in files)

    def test_get_files_dir_directories(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        os.chdir(project_dir)

        files = get_files_in_dir(".")
        self.assertEqual(len(files), 7)
        self.assertTrue("askanna.yml" in files)

    def test_get_files_dir_subdirectories(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        files = get_files_in_dir(".")
        self.assertEqual(len(files), 28)
        self.assertTrue("askanna.yml" in files)

    def test_get_files_in_dir_with_gitignore(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        files = get_files_in_dir(".", ignore_file=".gitignore")
        self.assertEqual(len(files), 21)
        self.assertTrue("askanna.yml" in files)
        self.assertTrue("data/input/input.csv" in files)
        self.assertFalse("data/interim/.gitkeep" in files)
        self.assertFalse("data/processed/input.csv" in files)
        self.assertFalse("data/processed/input-2.csv" in files)

    def test_get_files_in_dir_with_dotaskannaignore(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        files = get_files_in_dir(".", ignore_file=".askannaignore")
        self.assertEqual(len(files), 21)
        self.assertTrue("askanna.yml" in files)
        self.assertFalse("data/input/input.csv" in files)
        self.assertTrue("data/interim/.gitkeep" in files)
        self.assertFalse("data/processed/input.csv" in files)
        self.assertFalse("data/processed/input-2.csv" in files)

    def test_get_files_in_dir_with_askannaignore(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        files = get_files_in_dir(".", ignore_file="askannaignore")
        self.assertEqual(len(files), 22)
        self.assertTrue("askanna.yml" in files)
        self.assertFalse("data/input/input.csv" in files)
        self.assertFalse("data/interim/.gitkeep" in files)
        self.assertTrue("data/processed/input.csv" in files)
        self.assertTrue("data/processed/input-2.csv" in files)

    def test_get_files_paths_simple(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)

        files = get_files_in_paths(["."])
        self.assertEqual(len(files), 3)
        self.assertTrue("askanna.yml" in files)

        files = get_files_in_paths(["*"])
        self.assertEqual(len(files), 3)
        self.assertTrue("askanna.yml" in files)

    def test_get_files_paths_simple_single_file(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)

        paths = ["result.json"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("result.json" in files)

        paths = ["/result.json"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 0)  # because the file doesn't exist

    def test_get_files_paths_directories(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        os.chdir(project_dir)

        files = get_files_in_paths(".")
        self.assertEqual(len(files), 7)
        self.assertTrue("askanna.yml" in files)

    def test_get_files_paths_directories_dirs(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        os.chdir(project_dir)

        paths = ["data"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 2)
        self.assertTrue("data/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

        paths = ["data/*"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 2)
        self.assertTrue("data/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_paths_directories_single_file(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        os.chdir(project_dir)

        paths = ["model/model.pkl"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("model/model.pkl" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_paths_directories_unique_files(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        os.chdir(project_dir)

        paths = ["data", "/data", "data/"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 2)
        self.assertTrue("data/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

        paths = ["data", "/data", "data/", "data/dump.txt"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 2)
        self.assertTrue("data/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

        paths = ["/data", "model/model.pkl", "model/"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("model/model.pkl" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_paths_subdirectories(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        files = get_files_in_paths(".")
        self.assertEqual(len(files), 28)
        self.assertTrue("askanna.yml" in files)

    def test_get_files_paths_subdirectories_dirs(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        paths = ["data", "/data"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 5)
        self.assertTrue("data/processed/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_paths_subdirectories_single_file(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        paths = ["model/model.pkl"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 0)
        self.assertFalse("model/model.pkl" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_paths_subdirectories_unique_files(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        paths = ["data", "model/model.pkl", "model/"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 5)
        self.assertFalse("model/model.pkl" in files)
        self.assertTrue("data/processed/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_paths_subdirectories_dirs_formats(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        paths = ["data/input"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("data/input/input.csv" in files)
        self.assertFalse("data/processed/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

        paths = ["data/input/*"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("data/input/input.csv" in files)
        self.assertFalse("data/processed/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

        paths = ["/data/input"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 0)  # because the folder doesn't exist

        paths = ["data/input/"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("data/input/input.csv" in files)
        self.assertFalse("data/processed/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

        paths = ["data/input/*"]
        files = get_files_in_paths(paths)
        self.assertEqual(len(files), 1)
        self.assertTrue("data/input/input.csv" in files)
        self.assertFalse("data/processed/input.csv" in files)
        self.assertFalse("askanna.yml" in files)

    def test_get_files_from_excluded_paths(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        exclude_paths = [
            "/",
            "/bin",
            "/dev",
            "/lib",
            "/mnt",
            "/opt",
            "/proc",
            "/tmp",  # nosec: B108
            "/usr",
            "/var",
        ]

        paths = ["/"]
        files = get_files_in_paths(paths, exclude_paths)
        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)

        paths = ["/bin"]
        files = get_files_in_paths(paths, exclude_paths)
        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)

        paths = ["/var"]
        files = get_files_in_paths(paths, exclude_paths)
        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)

        paths = exclude_paths
        self.assertGreater(len(paths), 0)
        files = get_files_in_paths(paths, exclude_paths)
        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)

        paths = ["/", "."]
        files = get_files_in_paths(paths, exclude_paths)
        self.assertEqual(len(files), 28)
        self.assertTrue("askanna.yml" in files)
