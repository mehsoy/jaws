CREATE TABLE administrators ( 
        id integer PRIMARY KEY,
        FOREIGN KEY (id) REFERENCES users(id)
);
CREATE TABLE jobs (
        id integer PRIMARY KEY,
        priority integer,
        source_alias varchar,
        source_path varchar,
        target_alias varchar,
        user_name varchar,
        enqeued_at TEXT,
        started_at TEXT,
        ended_at TEXT,
        enqueued_at TEXT,
        status varchar,
        notification_abort boolean,
        notification_begin boolean,
        notification_end boolean,
        error varchar,
	    n_of_files integer,
	    n_of_dirs integer,
	    workpool_size integer,
	    compression_rate integer,
        target_path varchar,
    	copy_options varchar,

        FOREIGN KEY (user_name) REFERENCES users(name) 
);
CREATE TABLE managers_has_members (
        member_id integer,
        manager_id integer,

        PRIMARY KEY (member_id, manager_id)
);
CREATE TABLE project_managers (
        id integer,
        FOREIGN KEY (id) REFERENCES users(id)
);
CREATE TABLE storages (
    	alias varchar,
    	mountpoint varchar,
    	accept_jobs boolean,
	    has_home_dir boolean,
	    is_archive booolean,
	    max_extensions integer,
	    max_extension_period integer,
	    description varchar,
    	id integer PRIMARY KEY,
    	CONSTRAINT unique_name UNIQUE (alias) 
);
CREATE TABLE users (
        name varchar,
        token varchar,
        id integer PRIMARY KEY,
        user_type varchar,

        CONSTRAINT unique_name UNIQUE (name)
);
CREATE TABLE workers (
        id integer PRIMARY KEY,
        status varchar,
        current_job_id varchar,
        name integer,
        address varchar,
        FOREIGN KEY(current_job_id) REFERENCES jobs(id),
        CONSTRAINT unique_name UNIQUE (name)
);
CREATE TABLE workers_has_storages(
    worker_id integer,
    storage_alias integer,
    
   --  PRIMARY KEY (worker_id, storage_alias),
    FOREIGN KEY (worker_id) REFERENCES workers(id),
    FOREIGN KEY (storage_alias) REFERENCES storages(alias)
);

CREATE TABLE workspaces (
        id integer PRIMARY KEY,
        username varchar,
        label varchar,
        counter integer,
	    full_name, varchar,
        storage varchar,
        time_created TEXT,
        max_extension_period integer,
        max_extensions integer,
        times_extended integer,
        expiration_date TEXT,
	    status varchar,
        full_path TEXT,
        freetext TEXT,
        FOREIGN KEY (username) REFERENCES users(name),
        FOREIGN KEY (storage) REFERENCES storages(alias)
);
