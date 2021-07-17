import pytest

# Only directories can be moved. Trying to move a file should raise an error
from exceptions.not_a_directory_exception import NotADirectoryException
from worker.task import Task


def test_file_compress(centos127, archive1, outStub):
    with pytest.raises(NotADirectoryException):
        Task(1, centos127, 'johann-testfile-1.txt', archive1, outStub)


@pytest.mark.usefixtures('build_test_environment')
class TestTask:

    def test_compress_target_path_generation(self, archive1, dmd5, make_tar_task):
        task = make_tar_task(1, dmd5, 'test_dir-johann-1/', archive1)
        assert task.relative_source_path == 'test_dir-johann-1/'
        assert task.relative_target_path == 'johann-test_dir-1/'

    def test_extract_target_path_generation(self, archive1, dmd5, make_tar_task):
        task = make_tar_task(1, archive1, 'johann-secret_archive-1/', dmd5)
        assert task.relative_source_path == 'johann-secret_archive-1/'
        assert task.relative_target_path == 'secret_archive-johann-1/'

    def test_copy_target_path_generation(self, centos127, dmd5, make_rsync_task):
        # Notice, since a file called test_dir-johann-1 already exists in dmd5
        # the number is now incremented.
        task = make_rsync_task(1, centos127, 'johann-test_dir-1/', dmd5)
        assert task.relative_source_path == 'johann-test_dir-1/'
        assert task.relative_target_path == 'test_dir-johann-2/'
