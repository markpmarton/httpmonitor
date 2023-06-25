# python-26052023-markpmarton

# httpmonitor

A simple HTTP monitoring tool with limited scheduling and regex finding capabilities.
The scan result can be stored in a PostgreSQL database.

## Setup

The script has built-in setup automation function
but before running the schaffolding, the user needs to change the configuration file.
By default the is the _config.ini_ file.

### The default config file

```
[general]
working_dir = <folder for jobs. The setup script will generate it>

[database]
db_url = localhost                   --host url
db_port = 5432                       --host port
db_name = httpmonitor                --database name
db_name_default = defaultdb          --default database to connect first (during db and user creation)

[keyring]
service_name = httpmonitor           --service name for the password storage

[log]
out_path = <CWD>/log.log             --log output file
level = info                         --log level [info, debug, warning, error, critical]

```

After setting the config the following command will start the setup:

```
python -m httpmonitor --setup
```

The script is asking for the credentials to the superuser account of the database.
These credentials will be used only for the database schaffolding, after finishing the deploy these secrets will be removed from the key storage.

During the setup the script will create two roles in the database.

- A _Loader_ user for the inserting, updating, deleting queries (basically for all DML actions).
- And a _Retriever_ user for the select queries (DQL queries).

The setup prompt will ask for the credentials for these users.
Usernames must be at least 5 characters (max. 50) and the passwords must be at least 8 characters with 1 number and 1 special character.
If the keyring storage was never used on the target system before, the setup process might ask for for the system user password to unlocking the 'Default' keyring.

## Usage

The tool can run monitoring tasks (jobs) imported from the _jobs.json_ file or collect previously added jobs from the database.
To select reading from the json file, we need to run the httpmonitor command with the **--from_file** flag.

```
python -m httpmonitor --from-file
```

### The jobs.json file

The potencial monitoring jobs are stored in a JSON list:

Example jobs.json file

```

{
  "jobs": [
    {
      "name": "example_job",                            --name of the job (it must be unique, also with the already stored ones)
      "url": "https://cnn.com",                         --the target url (only the  http(s)://asd.xyz is allowed)
      "method": "GET",                                  --HTTP method
      "headers": {},                                    --HTTP headers in JSON format (ex. {"User-agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"})
      "body": {},                                       --HTTP body parameters in JSON format
      "expected_regex": "",                             --if regex detection is needed, the pattern can be registered in this field
      "scheduled_interval": 100                         --time interval between runs in seconds (5s-300s)
    },
    {
      "name": "job_4",
      "url": "https://foxnews.com",
      "method": "GET",
      "headers": {},
      "body": {},
      "expected_regex": "<article class=\"article-story-1\"[^>]+",
      "scheduled_interval": 15
    }
  ]
}

```

## Database

The setup script scaffolds the required database, schema and tables (the db name must be available).

### Structure

```
<db_name>.jobs:
    id: serial id pk,
    name: varchar(50) unique,
    url: varchar(100),
    method: varchar(10),
    headers: text,
    body: text,
    expected_regex: varchar(100),
    scheduled_interval: int

<db_name>.checks:
    id: serial id pk,
    job_id: int fk(jobs.id),
    start_ts: timestamp,
    end_ts: timestamp,
    status_code: int,
    regex_result_id: int fk(regex_raw.id)

<db_name>.regex_raw:
    id: serial id pk,
    raw_finding: text
```

## Sources

- Reusable logger factory: https://medium.com/geekculture/create-a-reusable-logger-factory-for-python-projects-419ad408665d
- Scheduling jobs with using the 'schedule' package: https://github.com/dbader/schedule)
