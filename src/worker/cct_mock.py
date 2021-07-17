from worker.consistency_check_tool import ConsistencyCheckTool
from worker.task import Task
from worker.task_status import TaskStatus


class CCTMock(ConsistencyCheckTool):
    """Mocks a ConsistencyCheckTool

    In case the Copytool doesn't employ a dedicated CCT.
    """

    def get_name(self):
        return 'MockingCheck'

    @staticmethod
    def consistency_check(task: Task, **kwargs):
        if task.status == TaskStatus.COPIED:
            task.status = TaskStatus.CHECKED
        return task
