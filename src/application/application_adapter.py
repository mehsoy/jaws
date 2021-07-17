""".. module:: apication_adapter"""
#!/usr/bin/python
#-*- coding: utf-8 -*-
import pwd

import os
import shutil

from application.copytools import determine_copytool
from application.handlers.acl_config_handler import ACLConfigHandler
from application.handlers.config_handler import ConfigHandler
from application.handlers.access_handler import AccessHandler
from application.handlers.response_builder import build_log, build_team_list, build_workers, build_workspaces, build_storages, build_job
from application.search import search_class
from application.search.posix import Posix
from application.search.search_class import initialize_storage_db
from application.search.search_class import check_tool_availability
from application.system.job import Job
from application.system.storage import Storage
from application.system.user import User, UserRole
import json

from application.system.workspaces import Workspaces
from master.master import Master


class Application:
    """
    Represents adapter pattern. Adapts json input from Controller to ApplicationFacade
    """

    def __init__(self, master=None, controller_mailbox=None):
        self.master = master if master else Master.get_master(mailbox=controller_mailbox)
        self.controller_mailbox = controller_mailbox
        self.config_handler = ConfigHandler()
        initialize_storage_db()
        check_tool_availability()
        self.access_handler = AccessHandler()
        acl_parser = ACLConfigHandler()

        #database access authorization
        self.table_to_class = dict(workspaces=Workspaces, storages=Storage)
        self.cls_to_identifier_method = { Workspaces: Workspaces.get_by_full_name,
                                          Storage: Storage.get_storage_by_name}
        self.cls_to_acl = {Workspaces: acl_parser.get_workspaces_setter_acl,
                           Storage: acl_parser.get_storages_setter_acl}

    def create_job(self, user, for_user, workspace, target, email):
        """
        :return: ID of a new Job
        :raises UserNotFoundException: if 'for_user' or 'user' doesn't exist in database
        :raises SearchException: Search raises an exception. See exception's message for details
        :raises StorageNotAcceptingException: if one of the referenced Storages doesn't accept jobs currently
        :raises NoAdministratorRightsException: if 'user' can not create jobs for 'for_user'
        :raises PermissionException: if 'for_user' reached his max. amount of jobs
        :raises MasterPausedException: if Master is paused
        """
        caller = User.get_user_by_username(user)
        for_user = User.get_user_by_username(for_user) if for_user else caller

        target_storj = Storage.get_storage_by_name(target)
        src_workspace = Workspaces.get_by_full_name(workspace)
        if src_workspace.username != caller.name and caller.get_user_type() != UserRole.Administrator:
            raise PermissionError('Unauthorized to move workspaces of other users.')
        src_storj = Storage.get_storage_by_name(src_workspace.storage)
        source = src_workspace.full_path
        addr = search_class.verify_job(source, target)
        target_path = target_storj.mountpoint + addr['source_relative_path']


        copy_options = determine_copytool(src_storj, target_storj)

        job = Job(addr['source_alias'], target, source, email, for_user, target_path=target_path, copy_options=json.dumps(copy_options))
        self.access_handler.check_create_job(job, caller)
        self.master.add_to_queue(job)
        return job.get_job_id()

    def cancel_job(self, job_id, user):
        """
        :raises JobNotFoundException: if there is no job with 'job_id'
        :raises UserNotFoundException: if 'user' doesn't exist
        :raises PermissionException: if 'user' is not permitted to cancel given job
        :raises SemanticException: if 'job' is already cancelled or done
        """
        job = Job.get_job_by_id(job_id)
        calling_user = User.get_user_by_username(user)
        self.access_handler.check_cancel_job(job, calling_user)
        self.master.cancel_job(job)

    def get_jobs(self, days, user=None, for_user=None, statuses=None):
        """
        :raises UserNotFoundException: if given 'user' or 'for_user' doesn't exist
        :raises NoProjectManagerRightsException: @see access_handler
        """
        calling_user = User.get_user_by_username(user) if user else None
        team = True if for_user == "team" else False
        for_user = None if for_user in [None, "team"] else User.get_user_by_username(for_user)

        if team:
            self.access_handler.check_read_rights(None, calling_user)
            jobs = Job.get_jobs(calling_user.get_team_members(), statuses, days)
        elif for_user is not None and calling_user is not None:
            self.access_handler.check_read_rights(for_user, calling_user)
            jobs = Job.get_jobs([for_user.get_username()], statuses, days)
        else:
            jobs = Job.get_jobs(None, statuses)

        return build_log(jobs)

    def get_directory_list(self, storage=None, user=None, for_user=None):
        """
        Routes get_directory_list request to ApplicationFacade and builds JSON
        :raises UserNotFoundException: if given 'user' or 'for_user' doesn't exist
        :raises NoProjectManagerRightsException: @see access_handler
        :raises StorageAliasNotFoundException: if 'storage' is not found.
        :raises StorageNotMountedException: if a Storage to be worked on is not currently mounted.
        :raises NoResponseFromSearchException: if Search is not reachable
        """
        calling_user = User.get_user_by_username(user) if user else None
        team = True if for_user == "team" else False
        for_user = None if for_user in [None, "team"] else User.get_user_by_username(for_user)
        if team:
            self.access_handler.check_read_rights(None, calling_user)
            users = calling_user.get_team_members()
        elif self.has_read_permission(calling_user, for_user):
            users = [for_user.get_username()] if for_user else None
        else:
            raise PermissionError("You have no access to this data!")
        return search_class.get_directory_list(storage_alias=storage, usernames=users)

    def get_storage_alias_list(self):
        """
        :return: list of available storages
        :raises NoResponseFromSearchException: if Search is not reachable
        """
        storage_aliases = [s.alias for s in Storage.get_storages()]
        return dict(storages=storage_aliases)

    def get_storages(self):
        return build_storages(Storage.get_storages())

    def get_storage(self, alias):
        return build_storages([Storage.get_storage_by_name(alias)])

    def get_job(self, user, job_id):
        """
        Routes get_job request to ApplicationFacade
        :raises UserNotFoundException: if given 'user' doesn't exist
        :raises NoProjectManagerRightsException: @see access_handler
        """
        calling_user = User.get_user_by_username(user)
        job = Job.get_job_by_id(job_id)
        for_user = job.get_user()
        self.access_handler.check_read_rights(for_user, calling_user)
        return build_job(job)

    def set_rights(self, user, role):
        """
        Routes set_rights request to ApplicationFacade.
        :raises UserNotFoundException: if given 'user' doesn't exist
        :raises PermissionException: @see access_handler
        """
        for_user = User.get_user_by_username(user)
        role = UserRole(role)
        self.access_handler.check_set_rights(for_user, role)
        for_user.set_user_type(role)

    def add_user_to_team(self, for_user, to_manager):
        """
        Routes add_user_to_team request to ApplicationFacade of another user (to_manager)
        """
        for_user = User.get_user_by_username(for_user)
        manager = User.get_user_by_username(to_manager)
        # @Todo test inheritance of get_user_by_username
        self.access_handler.check_add_user_to_team(for_user, manager)
        manager.add_user_to_team(for_user)

    def get_team_list(self):
        """
        Routes get_team_list request to ApplicationFacade
        """
        result = dict
        managers = User.get_users([UserRole.ProjectManager])
        for manager in managers:
            result.update({manager.get_username(): manager.get_team_members()})
        return build_team_list(result)

    def set_priority(self, job_id, priority):
        """
        Routes set_priority request to ApplicationFacade
        :raises JobNotFoundException: job with 'job_id' doesn't exist
        :raises PermissionException: job is not in the queue
        :raises MasterPausedException: if master is paused
        """
        job = Job.get_job_by_id(job_id)
        self.access_handler.check_set_priority(job)
        self.master.set_priority(job, priority)

    def get_workers(self):
        return build_workers(self.master.get_workers())

    def resume(self, job_id):
        """
        Routes resume request to ApplicationFacade
        """
        job = Job.get_job_by_id(job_id)
        self.access_handler.check_resume(job)
        self.master.resume_job(job)

    def verify_user_via_token(self, user, token):
        return self.access_handler.verify_user_via_token(user, token)

    def ensure_existance(self, user):
        return self.access_handler.ensure_existance(user)

    def get_user_type(self, user, as_string=True):
        user = User.get_user_by_username(user)
        if not as_string: return user.get_user_type()

        return user.get_user_type().name

    def enable_worker(self, worker_id):
        self.master.enable_worker(worker_id)

    def disable_worker(self, worker_id):
        self.master.disable_worker(worker_id)

    def get_credentials_by_user(self, user):
        user = User.get_user_by_username(user)
        self.access_handler.verify_user_via_token(user.name, None)
        token = user.get_token()
        return dict(token=token)

    def enable_master(self):
        self.master.is_active = True

    def disable_master(self, ):
        self.master.is_active = False

    def put_workspace_permission(self, username, label, counter, caller, tag_type, name, instruction):
        w = Workspaces.get_by_triple(username, label, counter)
        p = Posix(w.full_path)
        if caller is not None:
            if caller != p.get_owner():
                raise PermissionError('Insufficient permissions.')
        Posix(w.full_path).put_permission(tag_type, name, instruction)

    def get_workspace_permission(self, username, label, counter):
        w = Workspaces.get_by_triple(username, label, counter)
        return Posix(w.full_path).get_permission()

    def has_read_permission(self, calling_user, for_user):
        return (calling_user.get_user_type() == UserRole.Administrator
                or calling_user.get_username() == for_user.get_username())

    def get_workspaces(self, for_user):
        if for_user:
            return build_workspaces(Workspaces.get_by_username(for_user))
        else:
            return build_workspaces(Workspaces.get_all())

    def create_workspace(self, username, ws_label, storage_alias=None):
        if not storage_alias: storage_alias = self.config_handler.workspace_default_storage
        storj = Storage.get_storage_by_name(storage_alias)
        counter = Workspaces.calc_counter(ws_label, username)
        filename = self.config_handler.assemble_workspace_full_name(username, ws_label, counter)
        mnt = storj.mountpoint
        path = mnt + filename + '/'
        if os.path.exists(path): raise FileExistsError('workspace full_name naming collision, directory still exists')

        Workspaces(
            username=username,
            label=ws_label,
            storage=storage_alias,
            max_extension_period=storj.max_extension_period,
            max_extensions=storj.max_extensions,
            counter=counter
        )

        os.mkdir(path)
        uid = pwd.getpwnam(username).pw_uid
        os.chmod(path, 0o755)
        os.chown(path, uid, uid)
        w = Workspaces.get_by_triple(username, ws_label, counter)
        w.set_full_path(path)
        return w.full_name

    def remove_workspace(self, user, user_type, name):
        w = Workspaces.get_by_full_name(name)
        full_path = w.full_path
        full_name = w.full_name
        # if w.username == user or user_type is UserRole.Administrator:
        #     pass
        # else:
        #     raise PermissionError('Not allowed to remove workspace ' + w.full_name + '.')
        if not w.username == user and user_type is not UserRole.Administrator:
            raise PermissionError('Not allowed to remove workspace ' + w.full_name + '.')

        #remove ws from DB
        w.remove()
        #remove ws from fs
        if os.path.exists(full_path):
            try:
                shutil.rmtree(full_path)
                pass
            except OSError as e:
                return (full_name, "error: "+ e)
        else:
            return (full_name, "not found")

        return (w.full_name, "removed")

    def extend_workspace(self, user, user_type, name):
        w = Workspaces.get_by_full_name(name)
        if not w.username == user and user_type is not UserRole.Administrator:
            raise PermissionError('Not allowed to extend workspace ' + w.full_name + '.')
        w.extend()
        return (w.full_name, str(w.time_remaining))

    def set_in_database(self, table, key, value, identifier, user):
        # Strip down value to max 1024, probably should be improved
        value = value[:1024]
        user = User.get_user_by_username(user)
        cls = self.table_to_class[table]
        acl = self.cls_to_acl[cls]()
        if not key in acl[user.get_user_type()]:
            raise PermissionError('Users of type ' + user.get_user_type().name
                                  + ' are not allowed to set the ' + key + ' attribute in ' +table)
        meth = self.cls_to_identifier_method[cls]
        obj = meth(identifier)
        if not obj: raise AttributeError('No ' + table + ' with identifier ' + identifier + ' was found.')
        # Check if this operation, changing a users property (workspace), is authorized
        if cls.__name__ == 'Workspaces' and user.name != obj.username and user.get_user_type() != UserRole.Administrator:
            raise PermissionError('You are not allowed to modify the workspace ' + obj.full_name)
        obj.set_value(key, value)
