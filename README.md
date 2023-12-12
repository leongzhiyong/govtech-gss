# GitLab Instance Poller
This package was built for a technical assessment with the Government Technology Agency of Singapore.

## Prerequisites
- [Python >= 3.11](https://www.python.org/downloads/)

## Installation
Installation is optional; the package can be used directly from the source if desired.
Additionally, installation can be performed with [pip](https://pip.pypa.io/en/stable/getting-started/) via the pre-built distribution or directly from the source.

To install directly from the source, navigate to the package root and execute the installation.
```
$ cd /path/to/package
$ pip install --user .
```

To install from the pre-built distribution, navigate to the `dist/` directory and execute the installation with the wheel or the tarball.
You may need to install [wheels](https://pythonwheels.com/) first.
```
$ pip install --user wheel
$ cd /path/to/package/dist/
$ pip install --user gitlab-1.0.0-py3-none-any.whl # installing with wheel
$ # pip install --user gitlab-1.0.0.tar.gz # installing with tarball
```

## Usage
If you're using this package without installing, ensure that the commands are being executed from the package root.

### Setting up the database
In order to use the package, a database schema needs to be initialised first.
```
$ python -m gitlab migrate --database=/path/to/polls.db
```

The package opts to use SQLite as a simple, standlone database. The database file can be migrated with no concern, so long as
the appropriate file path is provided. Multiple database files can even be maintained, if some additional separation is desired.

Lastly, to check if the database schema migration is up to date
```
$ python -m gitlab check_migrations --database=/path/to/polls.db
```

### Poll a GitLab instance
Polling a GitLab instance can be performed as a one-off action or continuously.
Basic usage looks something like this:
```
$ python -m gitlab poll --url=https://my.gitlab.instance --database=/path/to/polls.db
```

To continously poll the instance, simply add the `--continuous` flag.
For example, to poll the instance every minute:
```
$ python -m gitlab poll --url=https://my.gitlab.instance --database=/path/to/polls.db --continuous
```

Additional execution options:
- `--token` : supply the GitLab access token directly; alternatively as the `GITLAB_ACCESS_TOKEN` environment variable.
- `--poll_interval` : interval (in seconds) between polls.
- `--save-responses` : record the full responses from the GitLab instance; helps with debugging but may bloat the database.

> There is a known issue when providing the GitLab access token via terminal prompt, whereby pasting from the clipboard with the CTRL+V keyboard shortcut may not work as expected. The package provides alternative instructions if it detects the bug.

### Export polling data
Polling persists data to the specified database, which can then be exported.
```
$ python -m gitlab export --output /path/to/output.csv --database=/path/to/polls.db
```

Additional execution options:
- `--url` : filter records to instances matching this URL.
- `--from` : filter records from this timestamp onwards.
- `--to` : filter records up to this timestamp.
- `--include-responses` : export the full responses saved during polling; response data only exists if the `--save-responses` flag is used during polling.

## Authors
Leo Ng (leong2108@gmail.com)
