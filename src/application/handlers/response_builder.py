#!/usr/bin/python
#-*- coding: utf-8 -*-
import json

def build_storages(storages):
    result = []
    for w in storages:
        d = w.__dict__
        del d['_sa_instance_state']
        result.append(d)
    return result

def build_workspaces(workspaces):
    result = []
    for w in workspaces:
        d = w.__dict__
        del d['_sa_instance_state']
        # Need to append hybrid properties to dict, since they are not in __dict__
        d['status'] = w.status
        d['time_remaining'] = str(w.time_remaining).split('.')[0]
        result.append(d)
    return result

def build_log(jobs):
    result = []
    for job in jobs:
        job_dictionary = {
            "job_id": job.get_job_id(),
            "source": job.get_source_alias() + ":" + job.get_source_path(),
            "target": job.get_target_alias(),
            "enqueue_time": job.get_enqueue_time().isoformat(),
            "creator": job.get_user().get_username(),
            "status": job.get_status().name,
            "error": job.get_error(),
        }
        job_dictionary["end_time"] = None if not job.get_end_time() else job.get_end_time().isoformat()

        result.append(job_dictionary)
    return result

def build_workers(workers):
    result = []
    for worker in workers:
        worker_dictionary = {
            "worker_id": worker.get_id(),
            "worker_name": worker.get_name(),
            "status": worker.get_status().name,
            "address": str(worker.get_address())
        }
        if worker.get_current_job() is not None:
            worker_dictionary["job"]["job_id"] = worker.get_current_job().get_job_id()
            worker_dictionary["job"]["target"] = worker.get_current_job().get_target_alias()
        result.append(worker_dictionary)
    return result

def build_job(job):
    dictionary = {
        "job_id": job.get_job_id(),
        "source": job.get_source_alias() + ":" + job.get_source_path(),
        "target": job.get_target_alias(),
        "enqueue_time": job.get_enqueue_time().isoformat(),
        "creator": job.get_user().get_username(),
        "status": job.get_status().name
    }
    return dictionary

def build_team_list(array):
    """Optional method for ProjectManager"""
    pass


class ResponseBuilder:
    """
    Builds JSON responses for Controller
    """
    def __init__(self):
        pass

    def build_create_job(self, job_id):
        """
        Creates JSON String with job_id
        Format:
            {
                "job_id": 1
            }
        :param job_id: Integer
        :return: String
        """
        dictionary = {'job_id': job_id}
        return self._build_json(dictionary)

    def build_user_role(self, user_role):
        """
        Creates JSON String with user_role.
        Format:
            {
                "role": "UserRole"
            }
        :param user_role: UserRole
        :return: String
        """
        dictionary = {'role': user_role.name}
        return self._build_json(dictionary)

    def build_exception(self, exception):
        pass

    def _build_json(self, dictionary):
        """
        Creates json String from dictionary.
        :param dictionary: dict
        :return: String
        """
        return json.dumps(dictionary)
