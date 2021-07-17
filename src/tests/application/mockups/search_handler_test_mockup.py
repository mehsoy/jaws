#!/usr/bin/python
#-*- coding: utf-8 -*-


class SearchHandler:
    """
    MockUp for component test of Application.
    """
    def __init__(self):
        pass

    def get_directory_list(self, for_users, target):
        return {"testtarget": ["directory1", "directory2", "directory3"]}

    def get_storage_list(self):
        return ["storage1", "storage2", "storage3"]

    def verify_job(self, source_abs_path, target_alias):
        return {"source_alias": "src",
                "source_relative_path": "srv"}

    def set_storage_accept_jobs(self, storage, mode):
        return

    def get_user_credentials(self, username):
        if username == "uyefv":
            return "token1"
        elif username == "verifyuser":
            return "token2"
        elif username == "verifyadmin":
            return "token3"
        return "token"

