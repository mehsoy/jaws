import os
import subprocess
import tarfile

import pytest

from worker.storage import Storage


@pytest.fixture(scope='module')
def archive1(default_tar):
    storage = Storage('archive1', '/mount/archive1', default_tar, '<username>-<dirname>-<number>', True)
    return storage


@pytest.fixture(scope='module')
def centos127(default_rsync):
    storage = Storage('centos', '/mount/centos127', default_rsync, '<username>-<dirname>-<number>', False)
    return storage


@pytest.fixture(scope='module')
def dmd5(default_rsync):
    storage = Storage('dmd5', '/mount/dmd5', default_rsync, '<dirname>-<username>-<number>', False)
    return storage


@pytest.fixture
def storages(archive1, centos127, dmd5):
    return [archive1, centos127, dmd5]


######################################################
# Warning: Don't terminate manually, while debugging #
# so the test environment is properly removed.       #
# Also check, if pytest application has permissions  #
######################################################
@pytest.fixture
def build_test_environment(centos127, dmd5, archive1):
    # build file structure for centos
    test_dir = centos127.mountpoint

    _mkdir(test_dir + "/bad_naming")

    _mkdir(test_dir + "/johann-test_dir-1")
    _mkfile(test_dir + "/johann-test_dir-1/testfile1.txt", "test successful\nother value")
    _mkfile(test_dir + "/johann-test_dir-1/testfile2.txt", "test successful")
    _mkdir(test_dir + "/johann-test_dir-1/subdir")
    _mkfile(test_dir + "/johann-test_dir-1/subdir/testfile1.txt",
            "test successful\nother value")
    _mkfile(test_dir + "/johann-test_dir-1/subdir/testfile2.txt", "test successful")

    # Build file structure for dmd5
    # Notice the different naming convention
    test_dir = dmd5.mountpoint
    _mkdir(test_dir + '/test_dir-johann-1')
    _mkfile(test_dir + '/test_dir-johann-1/dmd5file.txt', 'Boop')


    # build file structure for archive1
    test_dir = archive1.mountpoint
    _mkdir(test_dir + '/johann-secret_archive-1')
    _mkdir(test_dir + '/johann-secret_archive-2')

    # make a tarball in the johann-secret_archive-1 directory
    dirpath = test_dir + '/johann-secret_archive-1'
    _mkdir(dirpath + '/bible')
    _mkfile(dirpath + '/bible/jesus.txt', 'Let there be light.')
    _mkfile(dirpath + '/bible/maria.rc', 'And there was light.')
    with tarfile.open(test_dir + '/johann-secret_archive-1/johann-secret_archive-1.tar',
                      'w') as tar:
        tar.add(dirpath, arcname=os.path.sep)
    remove_file(dirpath + '/bible/jesus.txt')
    remove_file(dirpath + '/bible/maria.rc')

    yield

    for storage in [centos127, archive1, dmd5]:
        remove_subdirs(storage.mountpoint)


def remove_file(path: str):
    cmd = ["rm", "-f", path]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)


def remove_subdirs(path: str):
    cmd = " ".join(["rm", "-rf", path + '/*'])
    subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)


def _mkdir(path: str):
    cmd = ["mkdir", path]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)


def _mkfile(path: str, content: str):
    subprocess.check_output('echo "' + content + '" > ' + path, universal_newlines=True, shell=True)
