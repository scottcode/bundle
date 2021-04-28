import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

import pkg_resources
from pkg_resources import (
    resource_exists,
    resource_isdir,
    resource_listdir,
)

PACKAGE = 'bundle'

logger = logging.getLogger(__name__)

@dataclass
class WalkResult:
    name: str
    isdir: bool


def walk_resources(package_or_requirement, resource_name, path=()):
    logger.debug(
        "walk_resources called with package_or_requirement=%r, resource_name=%r, path=%r",
        package_or_requirement,
        resource_name,
        path,
    )
    if not any((resource_name, *path)):
        resource_path = ''
    else:
        resource_path = '/'.join((*path, resource_name))
    
    if resource_exists(package_or_requirement, resource_path):
        if resource_isdir(package_or_requirement, resource_path):
            _result = WalkResult(resource_path, isdir=True)
            logger.debug("Yielding %s", _result)
            yield _result
            add_to_path = (resource_name,) if resource_name else ()
            for item in resource_listdir(package_or_requirement, resource_path):
                yield from walk_resources(package_or_requirement, item, path=path+add_to_path)
        else:
            _result = WalkResult(resource_path, isdir=False)
            logger.debug("Yielding %s", _result)
            yield _result
    else:
        raise Exception(f"Resource not in package: {resource_path} not in {package_or_requirement}")

def copy_recursive(resource_name, target_dir, resource_path=()):
    writable = os.access(target_dir, mode=os.F_OK)
    if not writable:
        raise IOError(f"Target directory does not exist or not writable: {target_dir}")
    isdir = os.path.isdir(target_dir)
    if not isdir:
        raise IOError(f"target_dir is not a folder: {target_dir}")
    for item in walk_resources(PACKAGE, resource_name, path=resource_path):
        if item.isdir:
            os.mkdir(item.name)
        else:
            outpath = Path(target_dir, *resource_path, resource_name)
            infile = pkg_resources.resource_stream(PACKAGE, '/'.join((*resource_path, resource_name)))
            with open(outpath, 'wb') as outfile:
                shutil.copyfileobj(infile, outfile)
    

def test_walk_resources():
    resources = tuple(walk_resources('pandas', ''))
    pprint(resources)
    logger.info("Num resources found: %s", len(resources))
    assert len(resources) > 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_walk_resources()
