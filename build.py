#!/user/bin/env python3
import gzip
import logging
import os
from pathlib import Path
import shutil
import zipfile
import json
import re

import requests

import util

PATH_BASE = Path(__file__).parent.resolve()
PATH_BASE_MODULE: Path = PATH_BASE.joinpath("base")
PATH_BUILD: Path = PATH_BASE.joinpath("build")
PATH_DOWNLOADS: Path = PATH_BASE.joinpath("downloads")

MORPHIDA_REPO = "1013503897/Morphida"
PROJECT_REPO = "cainiao1992/magisk-morphida"
MODULE_ID = "magisk-morphida"
MODULE_NAME = "MagiskMorphida"

logger = logging.getLogger()
syslog = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
syslog.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(syslog)


def download_file(url: str, path: Path):
    file_name = url[url.rfind("/") + 1 :]
    logger.info(f"Downloading '{file_name}' to '{path}'")

    if path.exists():
        return

    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)

    logger.info("Done")


def extract_file(archive_path: Path, dest_path: Path):
    logger.info(f"Extracting '{archive_path.name}' to '{dest_path.name}'")

    with gzip.open(archive_path) as f:
        file_content = f.read()
        path = dest_path.parent

        path.mkdir(parents=True, exist_ok=True)

        with open(dest_path, "wb") as out:
            out.write(file_content)


# versionCode keeps the upstream scheme: frida version segments, zero-padded
# to 2 digits, plus a 2-digit build revision for repeated Morphida builds of
# the same frida version (e.g. 17.25.2 build 1 -> 17250201)
def generate_version_code(frida_tag: str, revision: int) -> int:
    parts = re.split(r"[-.]", frida_tag)
    version_code = "".join(f"{int(part):02d}" for part in parts) + f"{revision:02d}"
    return int(version_code)


def create_module_prop(path: Path, project_tag: str, frida_tag: str, revision: int):
    module_prop = f"""id={MODULE_ID}
name={MODULE_NAME}
version={project_tag}
versionCode={generate_version_code(frida_tag, revision)}
author=ViRb3 & enovella & 1013503897
updateJson=https://github.com/{PROJECT_REPO}/releases/latest/download/updater.json
description=Run frida-server on boot"""

    with open(path.joinpath("module.prop"), "w", newline="\n") as f:
        f.write(module_prop)


def create_module(project_tag: str, frida_tag: str, revision: int):
    logger.info("Creating module")

    build_tmp = PATH_BUILD.joinpath("tmp")
    if build_tmp.exists():
        shutil.rmtree(build_tmp)

    shutil.copytree(PATH_BASE_MODULE, build_tmp)
    create_module_prop(build_tmp, project_tag, frida_tag, revision)


def fill_module(morphida_tag: str):
    logger.info("Filling module for arch 'arm64'")

    # Morphida asset names use the plain frida version, without the -r suffix
    frida_tag = util.strip_build_id(morphida_tag)
    morphida_download_url = (
        f"https://github.com/{MORPHIDA_REPO}/releases/download/{morphida_tag}/"
    )
    morphida_server = f"frida-server-{frida_tag}-android-arm64.gz"
    morphida_server_path = PATH_DOWNLOADS.joinpath(morphida_server)

    download_file(morphida_download_url + morphida_server, morphida_server_path)
    files_dir = PATH_BUILD.joinpath("tmp", "files")
    files_dir.mkdir(exist_ok=True)
    extract_file(morphida_server_path, files_dir.joinpath("frida-server-arm64"))


def create_updater_json(project_tag: str, frida_tag: str, revision: int):
    logger.info("Creating updater.json")

    updater = {
        "version": project_tag,
        "versionCode": generate_version_code(frida_tag, revision),
        "zipUrl": f"https://github.com/{PROJECT_REPO}/releases/download/{project_tag}/{MODULE_NAME}-{project_tag}.zip",
        "changelog": f"https://raw.githubusercontent.com/{PROJECT_REPO}/master/CHANGELOG.md",
    }

    with open(PATH_BUILD.joinpath("updater.json"), "w", newline="\n") as f:
        f.write(json.dumps(updater, indent=4))


def package_module(project_tag: str):
    logger.info("Packaging module")

    module_zip = PATH_BUILD.joinpath(f"{MODULE_NAME}-{project_tag}.zip")
    build_tmp = PATH_BUILD.joinpath("tmp")

    with zipfile.ZipFile(module_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(build_tmp):
            for file_name in files:
                if file_name == "placeholder" or file_name == ".gitkeep":
                    continue
                zf.write(
                    Path(root).joinpath(file_name),
                    arcname=Path(root).relative_to(build_tmp).joinpath(file_name),
                )

    shutil.rmtree(build_tmp)


def do_build(morphida_tag: str, project_tag: str):
    PATH_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    PATH_BUILD.mkdir(parents=True, exist_ok=True)

    frida_tag = util.strip_build_id(morphida_tag)
    revision = util.count_build_tags(frida_tag) + 1

    create_module(project_tag, frida_tag, revision)
    fill_module(morphida_tag)
    package_module(project_tag)
    create_updater_json(project_tag, frida_tag, revision)

    logger.info("Done")
