import json
import logging
import shutil
import tomllib

from json import dump
from subprocess import run, CalledProcessError
from pathlib import Path
from argparse import ArgumentParser

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

_LOGGER = logging.getLogger("Version")

MANIFEST_PATH = Path('./custom_components/bbox/manifest.json')

def _run_uv_version_command(version: str):
    """ Function to run uv version command """
    _LOGGER.info("-> Updating project version")

    try:
        run(["uv", "version", version], check=True)
    except CalledProcessError as err:
        raise RuntimeError('Error happened during project version update', err.stderr.strip())

def _copy_version_in_ha_manifest(version: str):
    """ Function to copy version in ha manifest """
    _LOGGER.info("-> Updating manifest version")
    with MANIFEST_PATH.open("r+", encoding="utf-8") as manifest_json:
        manifest = json.loads(manifest_json.read())
        manifest["version"] = version

    with MANIFEST_PATH.open("w", encoding="utf-8") as manifest_json:
        json.dump(manifest, manifest_json, indent=2, ensure_ascii=False)

def _run_git_commit(version: str):
    """ Function to run git commit command """
    _LOGGER.info("-> Commiting project version commit")

    try:
        run(["git", "add", "uv.lock", "pyproject.toml", str(MANIFEST_PATH)], check=True)
        run(["git", "commit", "-m", f"Release {version}"], capture_output=True, check=True)
    except CalledProcessError as err:
        raise RuntimeError('Error happened during project version commit', err.stderr.strip())

def _run_git_tag(version: str):
    """ Function to run git tag command """
    _LOGGER.info("-> Commiting project version tag")

    try:
        run(["git", "tag", f"{version}"], capture_output=True, check=True)
    except CalledProcessError as err:
        raise RuntimeError('Error happened during project version tag', err.stderr.strip())

def main():
    """ Function to version project"""
    parser = ArgumentParser(description="Bump project version")
    parser.add_argument('version', help="New version of the project")

    arguments = parser.parse_args()
    version = arguments.version

    _LOGGER.info(f"⚙️ Bumping project version")
    _run_uv_version_command(version)
    _copy_version_in_ha_manifest(version)
    _run_git_commit(version)
    _run_git_tag(version)
    _LOGGER.info(f"✅ Project version bumped successfully to version {version}")

if __name__ == '__main__':
    main()