import builtins
import io
import os
import tempfile
import unittest
import uuid
from zipfile import ZipFile

import pytest

from askanna.config.utils import read_config
from askanna.core.utils.file import create_zip_from_paths, zip_files_in_dir
from askanna.core.utils.suuid import create_suuid


# Delete files created by the test function
# Source: https://stackoverflow.com/questions/51737334/pytest-deleting-files-created-by-the-tested-function
def patch_open(open_func, files):
    def open_patched(
        path,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None,
    ):
        if "w" in mode and not os.path.isfile(path):
            files.append(path)
        return open_func(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            closefd=closefd,
            opener=opener,
        )

    return open_patched


@pytest.fixture(autouse=True)
def change_dir_cleanup_files(monkeypatch):
    cwd = os.getcwd()

    files = []
    monkeypatch.setattr(builtins, "open", patch_open(builtins.open, files))
    monkeypatch.setattr(io, "open", patch_open(io.open, files))

    yield

    for file in files:
        os.remove(file)

    os.chdir(cwd)


def get_paths_from_config(job_name: str) -> list:
    config = read_config("askanna.yml")
    paths = config[job_name].get("output", {}).get("artifact", [])

    if isinstance(paths, str):
        paths = [paths]

    return paths


class TestZipFiles(unittest.TestCase):
    def setUp(self):
        tempdir = tempfile.mkdtemp(prefix="askanna-artifact")
        run_suuid = create_suuid(uuid.uuid4())
        self.zip_file = os.path.join(tempdir, f"artifact_{run_suuid}.zip")

    def test_zip_files_dir_simple(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)

        with ZipFile(self.zip_file, mode="w") as f:
            zip_files_in_dir(".", f)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 3)
        self.assertTrue("askanna.yml" in files)

    def test_zip_dir_directories(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        os.chdir(project_dir)

        with ZipFile(self.zip_file, mode="w") as f:
            zip_files_in_dir(".", f)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 7)
        self.assertTrue("askanna.yml" in files)

    def test_zip_dir_subdirectories_with_gitignore(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        os.chdir(project_dir)

        with ZipFile(self.zip_file, mode="w") as f:
            zip_files_in_dir(".", f, ignore_file=".gitignore")

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())
            print(files)

        self.assertEqual(len(files), 21)
        self.assertTrue("askanna.yml" in files)

    def test_zip_paths_simple(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        os.chdir(project_dir)

        paths = ["."]
        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 3)
        self.assertTrue("askanna.yml" in files)

    def test_zip_paths_simple_job_config_no_artifact(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        job_name = "test_job"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("result.json" in files)

    def test_zip_paths_simple_job_config_with_artifact(self):
        project_dir = "tests/fixtures/projects/project-001-simple"
        job_name = "test_job_artifact"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 1)
        self.assertFalse("askanna.yml" in files)
        self.assertTrue("result.json" in files)

    def test_zip_paths_directories_job_train_model(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        job_name = "train-model"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 2)
        self.assertFalse("askanna.yml" in files)
        self.assertTrue("data/input.csv" in files)
        self.assertTrue("data/input-2.csv" in files)

    def test_zip_paths_directories_job_select_best_model(self):
        project_dir = "tests/fixtures/projects/project-002-directories"
        job_name = "select-best-model"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 1)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertTrue("model/model.pkl" in files)

    def test_zip_paths_subdirectories_job_train_model(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        job_name = "train-model"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 28)
        self.assertTrue("askanna.yml" in files)
        self.assertTrue("data/input/input.csv" in files)
        self.assertTrue("models/model.pkl" in files)

    def test_zip_paths_subdirectories_job_create_dataset(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        job_name = "create_dataset"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 1)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertTrue("data/interim/.gitkeep" in files)

    def test_zip_paths_subdirectories_job_create_features(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        job_name = "create_features"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 3)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("data/dump.txt" in files)
        self.assertTrue("data/interim/.gitkeep" in files)
        self.assertTrue("data/processed/input-2.csv" in files)

    def test_zip_paths_subdirectories_job_serve_model(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        job_name = "serve-model"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertFalse("model/model.pkl" in files)

    def test_zip_paths_subdirectories_job_evaluate_model(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        job_name = "evaluate-model"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())
        # the test will have 0 files because the root folder is not allowed to be included in the list
        self.assertEqual(len(files), 0)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertFalse("models/model.pkl" in files)
        self.assertFalse("data/dump.txt" in files)
        self.assertFalse("data/interim/.gitkeep" in files)
        self.assertFalse("data/processed/input-2.csv" in files)

    def test_zip_paths_subdirectories_job_test_multiple_models(self):
        project_dir = "tests/fixtures/projects/project-003-subdirectories"
        job_name = "test multiple models"

        os.chdir(project_dir)
        paths = get_paths_from_config(job_name)

        create_zip_from_paths(self.zip_file, paths)

        with ZipFile(self.zip_file, "r") as f:
            files = set(f.namelist())

        self.assertEqual(len(files), 4)
        self.assertFalse("askanna.yml" in files)
        self.assertFalse("data/input.csv" in files)
        self.assertFalse("data/interim/.gitkeep" in files)
        self.assertTrue("models/model.pkl" in files)
        self.assertTrue("models/model-2.pkl" in files)
        self.assertTrue("models/benchmark_models_performance.png" in files)
        self.assertTrue("models/benchmark_models_time.png" in files)
