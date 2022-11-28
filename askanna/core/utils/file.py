import mimetypes
import os
from typing import List, Union
from zipfile import ZipFile

import click
import igittigitt


def zip_files_in_dir(directory_path: str, zip_file: ZipFile, ignore_file: Union[str, None] = None) -> None:
    # Zip the files that matches the filter from given directory
    files = get_files_in_dir(directory_path=directory_path, ignore_file=ignore_file)
    # Iterate over all the files and zip them
    for file in sorted(files):
        zip_file.write(file)


def get_files_in_dir(directory_path: str, ignore_file: Union[str, None] = None) -> set:
    file_list = set()

    ignore_parser = igittigitt.IgnoreParser()
    if ignore_file:
        ignore_parser.parse_rule_files(os.path.dirname(ignore_file), os.path.basename(ignore_file))

    # Iterate over all the files in directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Create complete filepath of file in directory
            file_path = os.path.join(root, file)
            if file_path.startswith("./"):
                file_path = file_path[2:]

            # can we add this file to the collection?
            if not ignore_parser.match(file_path):
                file_list.add(file_path)

    return file_list


def zip_paths(paths: List, zip_file: ZipFile, exclude_paths: List = []) -> None:
    files = get_files_in_paths(paths, exclude_paths)

    # Iterate over all the files and zip them
    for file in sorted(files):
        zip_file.write(file)


def get_files_in_paths(paths: List, exclude_paths: List = []) -> list:
    files = set()

    # first filter out empty string paths
    for path in filter(lambda x: len(x), paths):
        # replace asteriks if possible
        if path.startswith("*"):
            path = "." + path[1:]

        if path.endswith("/*"):
            path = path[:-1]

        if not os.path.exists(path):
            click.echo(f"{path} does not exists...skipping")
            continue

        # base folder path and check whether this is in the exclude_list
        base_folder = "/".join(path.split("/")[:2])
        if base_folder in exclude_paths:
            click.echo(
                f"[CONFIG ERROR] '{base_folder}' from '{path}' is on the exclusion list. AskAnna does not allow to "
                "access these files. This path is ignored and we continue with the other paths.",
                err=True,
            )
            continue

        if os.path.isdir(path):
            files.update(get_files_in_dir(path))
        else:  # so, we got a file
            if path.startswith("./"):
                path = path[2:]
            files.add(path)

    return sorted(files)


def create_zip_from_paths(filename: str, paths: List = []) -> None:
    """
    Create a ZipFile on the given `filename` location
    """
    # We exclude the following directories from included into the zip
    exclude_paths = [
        "/",
        "/bin",
        "/dev",
        "/lib",
        "/mnt",
        "/opt",
        "/proc",
        "/usr",
        "/var",
    ]

    with ZipFile(filename, mode="w") as f:
        zip_paths(paths, f, exclude_paths=exclude_paths)


def file_type(path):
    """Mimic the type parameter of a JS File object.
    Resumable.js uses the File object's type attribute to guess mime type,
    which is guessed from file extention accoring to
    https://developer.mozilla.org/en-US/docs/Web/API/File/type.
    Parameters
    ----------
    path : str
        The path to guess the mime type of
    Returns
    -------
    str
        The inferred mime type, or '' if none could be inferred
    """
    type_, _ = mimetypes.guess_type(path)
    # When no type can be inferred, File.type returns an empty string
    return "" if type_ is None else type_


def content_type_file_extension(content_type: str) -> str:
    content_type_file_extension_mapping = {
        "application/csv": ".csv",
        "application/json": ".json",
        "application/pdf": ".pdf",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/zip": ".zip",
        "image/jpeg": ".jpeg",
        "image/png": ".png",
        "text/plain": ".txt",
        "text/xml": ".xml",
    }

    file_extension = content_type_file_extension_mapping.get(content_type, ".unknown")

    return file_extension
