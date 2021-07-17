
Author: Mehmet Soysal (mehmet.soysal@kit.edu)
        Johann Mantel
        Jakob Ohm
        Adrian Beer
        Maximilian Beichter
        Anna Fedorchenko
        Dmytro Dehtyarov

JAWS (Just Another Workspace Suite)
==========
(Old Name DataMovementDaemon)



Installation
------------

Read SYSTEM_REQUIREMENTS.rst to make sure the host system is set up properly.


Usage
-----

Read INSTRUCTION_MANUAL.rst to learn how to use this tool.

TODO
----

0. unmunge_request should be renamed to authenticate and do exactly that. Right now authentication is spread accross
   two different functions (in controller) which is not good.


1. In Worker: Standardise stats dict ? e.g. stats as namedtuple

2. Copytools:
    - Find out how to get compression rates
    - Make parser to detect number of directories in tar output.
    - Add extra copytool action TAR_GZ to differentiate TAR and TAR_GZ files. (Shiftc cant handle .tar.gz files)

3. Webinterface:
    - make different base templates for admin and user
    - Show in navbar which section the user is currently located in
    - Dropdown to view specific storages in ``storages`` in web ui. Find html table extension (DataTable?)
        - show directories? -> may be too many. Show other stats like size etc.

4. Refactoring:
    - Make roles in controller and application a ENUM class instead of using Strings


Bugs:
-----
1. Database is initially ``read only``. Might be a problem if Controller is not started as root.

2. Database is not cleaned after running tests in tests/master which leads to errors on multiple runs.

3. If a worker is down, but has status "WAITING" in the database, the master will assign multiple jobs to the worker
   which is down.

4. Sometimes when an Exception is raised in Worker the Master isn't updated.

5. If the worker goes down with status "WAITNING" this will not be noticed by the master in so far as the job will
   be assigned "ACTIVE" status before an answer of the worker is received. Thus the jobs assigned to this worker will stay in "ACTIVE" state.
   This also implies that a worker can have multiple "ACTIVE" jobs
    - Proposal for solution: Add state "ASSIGNED" to JobStatus which currently comprise of "QUEUED", "ACTIVE", "DONE". This is to indicate that the job was assigned to a worker, but that the worker has not yet received a confirmation from the worker as to whether the worker has eccepted the job. Only when the worker updates the master will the master update the jobs status from "ASSIGNED" to "ACTIVE".
      If the worker doesn't answer his status should be set to "DOWN" or the like.

Weird Behavior:
---------------
 1. Make sure routes in the CmdView are correct and dont need to be redirected (e.g. caused by missing '/')

    - otherwise the redirect will mess up the request context in the before_request() call (don't know why),
      which is responsible for unmunging data, and result in a EMUNGE_CRED_REPLAYED Error in the controller.

 2. Sometimes (wasnt able to reproduce) directories just disappear during/after the move command. Extremenly rare. Cause unknown.


Misc:
---------------------
1. For copytool output to be parsed correctly certain options have to be enforced
   (e.g. --verbose --totals for tar & --stats for rsync)

2. The way in which the `number of files transferred` is generated with tar might lead to performance issues
(print line by line, then count lines)

5. 204 Responses can't contain a body so trying to unmunge it's body  will result in an error, but we need to
   evaluate the munge cred, otherwise an attacker could send the 204 Response falsely in place of the server?
   Put munge cred in query string or don't use 204 responses.
   - current fix: Check in send_request from helpers if response.text is None

6. Master and Application are intermingled and can't be on different nodes right now.

7. In Interfaces often a json object is passed as the argument to request(json=...), but the documentation states
    that the passed object only has to be json serializable, so the json strings in the body of e.g. POST requests
    were serialized to json twice and need to be deserialized twice.

8. The `workspace extend` command is a PUT HTTP request in "workspaces/" endpoint and the "workspace set" command a PATCH HTTP in "workspaces/<item>" endpoint. PUT is not the appropriate HTTP method and the "extend" command should address the same endpoint as the "set" command.