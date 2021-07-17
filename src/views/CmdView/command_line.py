#!/usr/bin/python
# -*- coding: utf-8 -*-


import argparse
import sys
import textwrap

from views.CmdView import activate, active, cancel, configuration, deactivate, job, log, workspace
from views.CmdView import ls_queue, storages, move, resume, rights, set_priority, tokenify, \
    workers, share, share_info


synonym_converter = {
    **dict.fromkeys(['workspaces', 'workspace'], 'workspace'),
    **dict.fromkeys(['storages', 'storage'], 'storages'),
    **dict.fromkeys(['config', 'configuration'], 'configuration')
}

class CommandLine(object):
    """
    Konstruktor of the CommandLine which takes the commands and arguments.
    By using argparse parsing the first argument the command and link it to a subparser for the
    command
    """

    def __init__(self):
        self.command = None
        parser = argparse.ArgumentParser(
            prog='PROG',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                '''The DataMovementDeamon - CommandLineTool 
                        
                ----- Currently available Command -----
                move, activate, active, cancel, configuration, deactivate,
                queue, job, log, resume, rights, resume, setPriority,
                workers, share, shareInfo, workspaces, storages                         
                                                                                                                                                   
            ''')
            ,
            usage='''dmd <command> [<args>]''')
        self.current_command = ' '.join([sys.argv[0].split('/')[-1]] + sys.argv[1:])
        parser.add_argument('command', help='Subcommand to run')
        arguments = parser.parse_args(sys.argv[1:2])

        new_command = synonym_converter.get(arguments.command)
        command = new_command if new_command else arguments.command

        if not hasattr(self, command):
            print('Unrecognized command : ' + sys.argv[1])
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, command)()

    def process(self):
        """
            subparser of the process command
        :return:
        """
        self.command.current_command = self.current_command
        self.command.execute(token=tokenify.Tokenify.getToken(),
                             username=tokenify.Tokenify.getUsername())

    def storages(self):
        """
            subparser of the lsTargets commmand
        :return:
        """

        parser = argparse.ArgumentParser(
            description='Returns all mounted Targets')
        subparsers = parser.add_subparsers(help='create a brand new workspace', dest='command')

        parser_list = subparsers.add_parser('list')

        group = parser_list.add_mutually_exclusive_group(required=False)
        group.add_argument('--user', type=str, action='store', help='Administration Command: '
                                                                   'For a '
                                                                   'specified User')
        group.add_argument('-a', '--all', action='store_true', help='Administration Command: For all '
                                                              'users')
        parser_list.add_argument('-d', '--dirs', action='store_true', help='show one level of dirs in the storage', default=False)
        parser_list.add_argument('--storage', type=str, help='Display the directories for a specific '
                                                      'storage')


        parser_set = subparsers.add_parser('set')
        parser_set.add_argument('keyvalue', help='specify <key>=<value>')
        parser_set.add_argument('alias', help='alias to specify the storage to alter.')

        args = parser.parse_args(sys.argv[2:])
        self.command = storages.Storages(None, args=args)

    def move(self):
        """
            subparser of the move command
        :return:
        """

        parser = argparse.ArgumentParser(
            description='Main command to move an source directory to an target!')

        parser.add_argument('workspace', type=str, help='workspace to be moved')
        parser.add_argument('target', type=str, help='Target alias destination')
        parser.add_argument('-a', action='store_true', help='Abort Message')
        parser.add_argument('-b', action='store_true', help='Beginn Message')
        parser.add_argument('-e', action='store_true', help='End Message')
        parser.add_argument('-user', action='store', dest='user',
                            help='Administration Command: Launching a move command for a '
                                 'specified User')

        args = parser.parse_args(sys.argv[2:])

        if hasattr(args, 'user'):
            self.command = move.Move(workspace=args.workspace, target=args.target, obj=None, a=args.a,
                                     b=args.b, e=args.e,
                                     user=args.user)
        else:
            self.command = move.Move(workspace=args.workspace, target=args.target, obj=None, a=args.a,
                                     b=args.b, e=args.e)

    def activate(self):
        """
            subparser of tje activate command
        :return:
        """
        parser = argparse.ArgumentParser(
            description="Administration Command: Used for activate a paused Worker/Master"
        )
        parser.add_argument('object', type=str, help='Type to activate worker/master')
        parser.add_argument('--id', type=str, help='Id ')
        args = parser.parse_args(sys.argv[2:])

        self.command = activate.Activate(obj=None, id=args.id, object=args.object)

    def active(self):
        """
            subparser of the active command
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Returns all active Jobs')
        parser.add_argument('-user', type=str, action='store',
                            help='Administration Command : For a specified User')
        parser.add_argument('-all', action='store_true',
                            help="Administration Command : Returns all active jobs from everyone")
        args = parser.parse_args(sys.argv[2:])
        self.command = active.Active(None, user=args.user, all=args.all)

    def cancel(self):
        """
            subparser of the cancel command
        :return:
        """

        parser = argparse.ArgumentParser(
            description='Cancels a job with id x')
        parser.add_argument('id', type=int, help='Id of the Job')
        args = parser.parse_args(sys.argv[2:])
        self.command = cancel.Cancel(obj=None, id=args.id)

    def deactivate(self):
        """
            subparser of the deactivate command

        :return:
        """
        parser = argparse.ArgumentParser(
            description="Administration Command: Used for deactivate a paused "
                        "Worker/Master"
        )
        parser.add_argument('object', type=str, help='Type to deactivate worker/master')
        parser.add_argument('--id', type=str, help='Id ')
        args = parser.parse_args(sys.argv[2:])

        self.command = deactivate.Deactivate(obj=None, id=args.id, object=args.object)

    def queue(self):
        """

        :return:
        """

        parser = argparse.ArgumentParser(
            description='Returns all aktive Jobs')
        args = parser.parse_args(sys.argv[2:])
        self.command = ls_queue.LsQueue(None)

    def job(self):
        """
            subparser of the job command
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Shows information of a job ')
        parser.add_argument('id', type=int, help='Id of the Job')
        args = parser.parse_args(sys.argv[2:])
        self.command = job.Job(obj=None, id=args.id)

    def log(self):
        """
            subparser of the log command
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Shows the Logs')
        parser.add_argument('days', type=int, help='Days in the past')
        parser.add_argument('-user', type=str,
                            help='Administration Command : For a specified User')
        args = parser.parse_args(sys.argv[2:])
        self.command = log.Log(obj=None, days=args.days, user=args.user)

    def configuration(self):
        """
            subparser of the log command
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Show the configuration')
        parser.add_argument('configfile', type=str, help='show corrosponding configuration')
        args = parser.parse_args(sys.argv[2:])
        self.command = configuration.Configuration(obj=None, configfile=args.configfile)

    def resume(self):
        """
            subparser of the resume command
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Resumes a job ')
        parser.add_argument('id', type=int, help='Id of the Job')
        args = parser.parse_args(sys.argv[2:])
        self.command = resume.Resume(obj=None, id=args.id)

    def rights(self):
        """
                    subparser of the rigths command
                :return:
                """

        parser = argparse.ArgumentParser(
            description='Sets a role , possible Roles are Administrator and User')
        parser.add_argument('username', type=str, help='Username to set role')
        parser.add_argument('role', type=str, help='Rolename to set')
        args = parser.parse_args(sys.argv[2:])
        self.command = rights.Rights(obj=None, role=args.role, user=args.username)

    def setPriority(self):
        """
            subparser of the setPriority command
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Sets a priority of a job ')
        parser.add_argument('priority', type=int, help='Priority Value')
        parser.add_argument('id', type=int, help='Id of the job')
        args = parser.parse_args(sys.argv[2:])
        self.command = set_priority.SetPriority(obj=None, priority=args.priority, id=args.id)

    def workers(self):
        """
            subparser of the worker command
          :return:
        """

        parser = argparse.ArgumentParser(
            description='Returns all active Jobs')
        args = parser.parse_args(sys.argv[2:])
        self.command = workers.Workers(None)

    def share(self):
        parser = argparse.ArgumentParser(
            description='To share and manage access rights of a workpool'
        )
        parser.add_argument('type', choices=['other', 'group', 'user'], help='type of the entity')
        parser.add_argument('name', default=None, nargs='?',
                            help='name of the entity, if type is not \'other\'')
        parser.add_argument('--chmod', type=str, default='+rx',
                            help='''Mode changes to be applied the the entity.\nTo delete 
                            certain rights from the ACL following syntax has to be 
                            utilized:\n\tdmd share --chmod=-r''')
        parser.add_argument('full_name', type=str, help='the full_name of a workspace')
        args = parser.parse_args(sys.argv[2:])
        self.command = share.Share(obj=None, tag_type=args.type, name=args.name,
                                   instruction=args.chmod, full_name=args.full_name)

    def shareInfo(self):
        parser = argparse.ArgumentParser(
            description='Displays information about access rights of a workpool'
        )
        parser.add_argument('full_name', type=str, help='the full_name of a workspace')
        args = parser.parse_args(sys.argv[2:])
        self.command = share_info.ShareInfo(obj=None, full_name=args.full_name)

    def workspace(self):
        """
            subparser of tje activate command
        :return:
        """
        parser = argparse.ArgumentParser(
            description="Manages your workspaces."
        )
        subparsers = parser.add_subparsers(help='create a brand new workspace', dest='command')
        parser_create = subparsers.add_parser('create')
        parser_create.add_argument('label', help='the label of the workspace')
        # parser_create.add_argument('--storage',
        #                            help='storage where the workspace is going to be placed initially')

        parser_list = subparsers.add_parser('list')
        parser_list.add_argument('--all', action='store_true', help='lists all workspaces; needs appropiate priviliges')
        # parser_list.add_argument('filters', nargs='*')

        parser_extend = subparsers.add_parser('extend')
        parser_extend.add_argument('full_name', help='full_name of the workspace')
        #TODO: add to web interface
        parser_extend = subparsers.add_parser('remove')
        parser_extend.add_argument('full_name', help='full_name of the workspace')

        parser_set = subparsers.add_parser('set')
        parser_set.add_argument('keyvalue', help='specify <key>=<value>')
        parser_set.add_argument('full_name', help='full_name to specify the workspace to alter.')

        args = parser.parse_args(sys.argv[2:])
        self.command = workspace.Workspace(obj=None, args=args)
