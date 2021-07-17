from exceptions.action_not_supported_exception import ActionNotSupportedException
from exceptions.copy_fail_error import CopyFailError

from worker.action import Action
from worker.copytool.copytool import Copytool
from worker.task import Task
from worker.task_status import TaskStatus

'''
Some comments on the tool:
 - When extracting a normal .tar file it is able to do so, but an error regarding the checksum
 occurs: `Unable to compute destination hash`
 
 - When trying to extract a .tar.gz, i.e. a with gzip compressed dir it is not able to do so 
 with he  following error message:
 `Unable to read header at offset 0 in tar file `
 
 - After unzipping the .tar.gz shiftc can then successfully extract the .tar file.
 -> This means shiftc can't extract gzip tars.
 
 - shiftc stores relative path of the proces inside tar, so we have to switch to source_dir
 during the copy process.

'''


class Shiftc(Copytool):

    @property
    def SUPPORTED_ACTIONS(self, ):
        return [
            Action.COPY,
            Action.EXTRACT_TAR,
            Action.COMPRESS_TAR,
        ]

    @staticmethod
    def get_name():
        return 'shiftc'

    def create_cmd(self, task: Task):
        cmd = []
        cmd.append(self._executable_path)
        # --wait also ensures statitic in the output
        cmd.append('-d')
        cmd.extend(['--no-verify', '--wait'])

        if task.action == Action.EXTRACT_TAR:
            # cmd.append('-r')  # copy directories recursively

            for option in self._options.split(" "):
                cmd.append(option)
            cmd.append('--extract-tar')
            cmd.append(task.absolute_source_path + '*')
            cmd.append(task.absolute_target_path)

        elif task.action == Action.COMPRESS_TAR:
            #  Make sure we are inside the correct directory. Otherwise parent
            # directory structure will be stored inside tarballs, which must be avoided.
            cmd[0:0] = ['cd', task.absolute_source_path, '&&']
            cmd.append('-r')  # copy directories recursively

            for option in self._options.split(" "):
                cmd.append(option)
            cmd.append('--create-tar')
            cmd.append('*')
            cmd.append(task.absolute_target_path + (task.absolute_target_path.split('/')[-2]))

        elif task.action == Action.COPY:
            # copy recursively
            cmd.append('-r')
            # so we dont include the source dirname in the copied filenames
            cmd.append('--no-target-directory')
            cmd.append(task.absolute_source_path)
            cmd.append(task.absolute_target_path)

        else:
            raise ActionNotSupportedException()
        return cmd

    @classmethod
    def parse_stats(cls, output: str):
        stats = dict()
        stats['n_of_dirs'], stats['n_of_files'], stats['total_size'] = cls._parse_lines(output)
        stats['n_of_files'] += stats['n_of_dirs']
        return stats

    @staticmethod
    def _parse_lines(string):
        fields = string.split('+')[-1].split('|')

        def convert_to_bytes(s: str):
            number = int(''.join(filter(str.isdigit, s.split('.')[0])))
            unit = ''.join(filter(str.isalpha, s.split('.')[0]))
            unit_converter = {'ZB': 10 ** 21,
                              'EB': 10 ** 18,
                              'PB': 10 ** 15,
                              'TB': 10 ** 12,
                              'GB': 10 ** 9,
                              'MB': 10 ** 6,
                              'KB': 10 ** 3,
                              'B': 10 ** 0}
            return unit_converter[unit] * number

        return tuple(
            [int(fields[2].split('/')[0]),
             int(fields[3].split('/')[0]),
             convert_to_bytes(fields[4].split('/')[0])])

    def handle_error(self, retcode, cmd, output, task):
        task.add_error(
            CopyFailError(Copytool.STANDARD % (task.worker_name, task.get_id(), output)))
        task.status = TaskStatus.ERROR
        return task
