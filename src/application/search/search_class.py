#!/usr/bin/python
#-*- coding: utf-8 -*-

import subprocess

import sys
import os
import threading
import queue

from application.system.storage import Storage
from exceptions.system_setup_error import SystemSetupError

from exceptions.storage_not_mounted_error import StorageNotMountedError
from exceptions.storage_not_mounted_exception import StorageNotMountedException
from exceptions.source_path_not_valid_exception import SourcePathNotValidException
from exceptions.storage_type_compatibility_exception import StorageTypeCompatibilityException
from exceptions.storage_not_accepting_exception import StorageNotAcceptingException
from exceptions.user_not_found_exception import UserNotFoundException

from application.handlers.config_handler import initialize_storages_from_config


def initialize_storage_db():
    initialize_storages_from_config()
    check_storages_mount(Storage.get_storages())

def get_directory_list(usernames: [str], storage_alias: str = None):
    """Searches given Storage for all Data created by users with given usernames and returns a dictionary where keys are storage aliases and values are lists with relative adresses of directories.

    :param storage_alias: the unique string Alias of the Storage to be searched (default = None).
    :param usernames: a List of usernames.

    :raises StorageAliasNotFoundException: if storage_alias is not found.
    :raises StorageNotMountedException: if a Storage to be worked on is not currently mounted.
    """
    storage_list = []
    #  We search all the Storages
    if storage_alias is None:
        storage_list = Storage.get_storages()
    #  We search only the specified Storage
    else:
        storage_list.append(Storage.get_storage_by_name(storage_alias))

    #  search for directories in selected storages
    directories = dict()
    for storage in storage_list:
        #  assure the storage is accessible
        if not (check_storage_mount(storage)):
            raise(StorageNotMountedException("The Storage with the alias >>" + storage.alias +
                                             "<< is currently not mounted under " + storage.mountpoint))
        abs_paths = search_for_directories(storage, usernames)
        rel_paths = []
        for abs_path in abs_paths:
            rel_paths.append(resolve_abs_address(abs_path)[1])
       # Eliminate storages without directories to show only if storage_alias is None
       #if storage_alias is None and len(abs_paths) == 0:
        #    pass
        #else:
        directories[storage.alias] = rel_paths
    return directories

def resolve_abs_address(source_path: str):
    """Searches a Storage with same mountpoint as source_paths beginning and returns a List
    [storage_alias, source_rel_path].
    If there is a conflict (storage1.mountpoint being substring of storage2.mountpoint) the storage with longest
    mountpoint will be selected.

    :param source_path: The path to be split into storage_alias and relative_path.

    :raises SourcePathNotValidException: if no matching Storage is found.
    """
    if not os.path.exists(source_path):
        raise(SourcePathNotValidException("The path " + source_path +
                                          " does not exist on the system."))
    match_list = []
    for storage in Storage.get_storages():
        #  test if both start with same path
        if source_path.startswith(storage.mountpoint):
            match_list.append(storage)
    if len(match_list) == 0:
        #  executed only if we found no matching storage
        raise(SourcePathNotValidException("The path " + source_path +
                                          " does not match any registered Storages mountpath."))
    else:
        #  select storage with longest mountpoint
        maxlen = 0
        match_storage = None
        for storage in match_list:
            if len(storage.mountpoint) > maxlen:
                maxlen = len(storage.mountpoint)
                match_storage = storage
        # strip the mount point
        source_rel_path = source_path[len(match_storage.mountpoint):]
        return [match_storage.alias, source_rel_path]

def verify_job(source_absolute_path: str, target_alias: str):
    """If the job is valid, returns a List [source_alias, source_rel_path, target_alias].
    Else throws an Exception.

    :param source_absolute_path: The path of the directory to be moved.
    :param target_alias: The alias of the Storage the directory is to be moved to.

    :raises SourcePathNotValidException: if the path does not exist in the system.
    :raises SourcePathNotValidException: if no Storage mounted at source_absolute_paths beginning.
    :raises StorageAliasNotFoundException: if no Storage with target_alias is found.
    :raises StorageNotMountedException: if either one of the involved Storages is not currently mounted.
    :raises StorageTypeCompatibilityException: if the Storage types of source and target are incompatible.
    :raises StorageNotAcceptingException: if one of the referenced Storages doesn't currently accept jobs.
    """
    if not os.path.isdir(source_absolute_path):
        raise(SourcePathNotValidException("The path " + source_absolute_path + " is not a directory."))
    src_alias, source_rel_path = resolve_abs_address(source_absolute_path)
    target_storage = Storage.get_storage_by_name(target_alias)
    source_storage = Storage.get_storage_by_name(src_alias)
    if target_storage is None: raise AttributeError('Storage with alias ' + target_alias + ' not found.')

    verify_target(source_storage)
    verify_target(target_storage)

    if not check_storage_type_compatibility(source_storage, target_storage):
        raise(StorageTypeCompatibilityException("The storage Types are not compatible."))
    if not source_storage.accept_jobs:
        raise(StorageNotAcceptingException("The Storage " + source_storage.alias +
                                           " does not currently accept jobs."))
    elif not target_storage.accept_jobs:
        raise(StorageNotAcceptingException("The Storage " + target_storage.alias +
                                           " does not currently accept jobs."))
    else:
        return  {
                'source_alias' : source_storage.alias,
                'source_relative_path': source_rel_path,
                'target_alias' : target_storage.alias
                }

def check_storage_mount(storage):
    """Return True if mount_path of given Storage is a mount point: a point in a file system where a
    different file system has been mounted.

    :param storage: the Storage to be checked for mount."""
    return check_storages_mount([storage])

def check_storage_type_compatibility(source_storage,
                                     target_storage):
    """Checks if the storages are compatible or not."""
    return not (source_storage.is_archive and target_storage.is_archive)

def get_user_credentials(username: str):
    """Performs a lookup in the home directory of username and returns the credentials-string if found.

    :raises StorageNotMountedException: if any Storage with homedirectory is not currently mounted.
    :raises UserNotFoundException: if there was no lookup result.
    """
    home_storages = _get_home_storages()
    #iterate over home directories searching for user
    for storage in home_storages:
        credentials = _get_user_credentials(username)
        if(credentials != None):
            return credentials
    #if we get here no user was found
    raise(UserNotFoundException("The home directory of " + username + " could not be found."))

def verify_target(storage):
    """Returns the Storage of given alias if it is valid or throws an Exception.

    :raises StorageAliasNotFoundException: if no storage with given alias is found.
    :raises StorageNotMountedException: if the storage exists, but is not mounted currently.
    """
    if check_storage_mount(storage):
        return storage
    else:
        raise StorageNotMountedException("The Storage with the alias >>" + storage.alias +
                                            "<< is currently not mounted under " + storage.mountpoint)

def _get_home_storages():
    """Returns a List of all mounted Storages with home directories."""
    home_storages = Storage.get_home_storages()
    for storage in home_storages:
        #  assure the storages we want to work on actually function ;)
        if not check_storage_mount(storage):
            raise(StorageNotMountedException("The Storage with the alias >>" + storage.alias +
                                        "<< is currently not mounted under " + storage.path))
    return home_storages


def check_storages_mount(storages):
    """
    Checks whether the given storages are mounted.

    :param storages: storages which mountpoints are to be checked
    """
    bucket = queue.Queue()
    new_thread = MountcheckThread(bucket, storages)
    new_thread.start()
    new_thread.join(10)
    try:
        exc = bucket.get(block=False)
        exc_type, exc_obj, exc_trace = exc
        if exc:
            if exc_type is StorageNotMountedError:
                raise exc_obj
    except queue.Empty:
        pass
    if new_thread.isAlive():
        raise Exception("Timeout for checking mountpoints was exceeded")
    return True

def check_tool_availability():
        #a hacky way to check if command is possible, necessary because we use shell=True later:
        try:
            subprocess.check_output(["getent", "--help"])
        except OSError as os_err:
            raise(SystemSetupError("In search_storage.get_user_credentials: "
                                    + "Could not execute getent, the program was not found."
                                    + " Please make sure to have it installed. The Error message was:\n"
                                    + str(os_err)))
        except Exception:
            pass
        try:
            subprocess.check_output(["cut", "--help"])
        except OSError as os_err:
            raise(SystemSetupError("In search_storage.get_user_credentials: "
                                    + "Could not execute cut, the program was not found."
                                    + " Please make sure to have it installed. The Error message was:\n"
                                    + str(os_err)))
        except Exception:
            pass

def _get_user_credentials(username):
    """Search for a home directory called username and look for the credentials file inside of it.

    :param username: the name of users homedirectory
    :raises SystemSetupError: if a needed unix program is not found.
    :return: the credentials string or None if no file was found.
    """
    #now, we execute the command we realy wanted to
    try:
        home_path = subprocess.check_output('getent passwd "' + username + '" | cut -d: -f6',
                                            universal_newlines = True, shell = True)
        #delete /n at the end of the string
        home_path = home_path[:-1]
    #except CalledProcessError as process_err:
    #    pass
    except OSError as os_err:
        raise(SystemSetupError("In search_storage.get_user_credentials: "
                                + "Could not execute /bin/sh, the program was not found."
                                + " Please make sure to have it installed. The Error message was:\n"
                                + str(os_err)))
    if home_path == "":
        raise(UserNotFoundException("The user with name " + username + " was not found."))
    #use home_path to find credentials now
    with open(home_path + "/.dmd/config/credentials.txt") as f:
        token = f.readline()
    token = token.rstrip('\n')
    return token

def search_for_directories(storage, usernames):
    """Searches the storage for subdirectories created by one of given usernames and returns a list of
    their respective absolute path.

    :param usernames: The usernames to be looked after in self.mountpoint.
    :return: the directories starting with a username in <usernames>
    """
    filelist = os.listdir(storage.mountpoint)
    directories = [f for f in filelist if os.path.isdir(os.path.join(storage.mountpoint,f))]

    if not usernames:
        return [os.path.join(storage.mountpoint, x)for x in directories]

    return [os.path.join(storage.mountpoint, d) for d in directories if any([u for u in usernames if u in d])]



class MountcheckThread(threading.Thread):
    """
    Threadclass made specifically for checking whether storages are mounted.

    :raises StorageNotMontedError: If a Storage is not mounted at its given mountpath.
    """

    def __init__(self, bucket, storages):
        """
        Constructor of the class.

        :param bucket: queue where possible errors are put in order to get them in the main thread
        :param storages: storages which mountpoints are to be checked
        """
        threading.Thread.__init__(self)
        self.bucket = bucket
        self.storages = storages

    def run(self):
        try:

            for storage in self.storages:
                if not (os.path.ismount(storage.mountpoint)):
                    raise StorageNotMountedError('Application', storage.mountpoint)
        except StorageNotMountedError:
            self.bucket.put(sys.exc_info())
