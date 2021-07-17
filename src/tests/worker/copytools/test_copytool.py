# import pytest
#
# @pytest.mark.usefixtures('build_test_environment')
# class TestCopytool:
#
#     def test_delete(self, centos127, dmd5, make_rsync_task):
#         task = make_rsync_task(1, centos127, 'johann-test_dir-1/', dmd5)
#         task.copytool.copy(task)
#
#         task.set_status_force(TaskStatus.CHECKED)
#         # (CopyProcessFailedException):
#         task = task.copytool.delete(task)
#         assert task.status == TaskStatus.EXCEPTION
#         assert isinstance(task.get_exceptions()[0], CopyProcessFailedException)
#
#
# def test_delete_dir(task_dir):
#     """Checks if delete does handle blocked files correctly."""
#     task = task_dir
#     task = TestHelper.block_source_file(task)
#     task.status = TaskStatus.CHECKED
#     # (CopyProcessFailedException):
#     task = task.copytool.delete(task)
#     assert task.status == TaskStatus.EXCEPTION
#     assert isinstance(task.get_exceptions()[0], CopyProcessFailedException)
#     task = TestHelper.unblock_source_file(task)
#
#

#
# def test_readonly(task_readonly):
#     """Try to write to a readonly directory."""
#     task = task_readonly
#     # (CopyFailError):
#     task = task.copytool.copy(task)
#     assert task.status == TaskStatus.ERROR
#     assert isinstance(task.get_errors()[0], CopyFailError)
#     assert os.path.exists(task.absolute_target_path) == False