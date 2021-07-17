

Installation of the DMD Servers:
---------------------------------------------

1) Installation of the virtual environment:
    (Make sure you checked out SYSTEM_REQUIREMENTS.rst first)

    .. code-block::

        $ pipenv install

2) Depending on the node configure the files in cfg/. You can also select a different location for the config directory
   in /etc/default/dmd or simply put the directory in .dmd/ in your home directory.

.. warning::
    Die storages muessen jeweils auf dem search und den worker Knoten separat konfiguriert werden.
    Bei Updates (z.B. der naming convention) mussen dann alle beide Konfigurationsdateien entsprechend geaendert werden.

3) Installing the SQL-Database (only on controller & master node):
    Execute the following command in the directory src/database:

    .. code-block::

        $ sqlite3 dmd_data.sqlite3 < create.sql


Starting a Server:
-------------------------------


1) To activate the virtual environment or run a command inside the virtual environemnt respectively:

.. code-block::

    $ pipenv shell
    $ pipenv run <command>

2) A nodes can be started by running one of these commands inside the virtual environment:


.. code-block::

    $ dmdcontroller
    $ dmdmaster
    $ dmdsearch
    $ dmdworker

.. warning::

    Make sure the worker and search servers have the necessary rights to access the user's credential.txt file and
    to modify files in the mountpoints. The controller also needs to have root privileges for the web application to
    work.

Installing the DMD from a Users Perspective:
--------------------------------------------

1) Run the  python file ``create_credentials.py`` to generate a credentials.txt file in the users home directory.

2) Install and activate the virtual environment.

3) Run a command e.g. ``dmd lsTargets``. This will register the user in the database. Now the user can use the dmd to his wishes.

