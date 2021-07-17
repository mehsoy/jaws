
class ControllerMailbox:

    def __init__(self, socket_io):
        self.socket = socket_io

    def update_worker(self, worker):
        # TODO this is only stub for tests
        self.socket.emit('worker_update', {'worker_id': worker}, namespace='/web/admin/dashboard')
        print('A new worker_update was pushed.')

